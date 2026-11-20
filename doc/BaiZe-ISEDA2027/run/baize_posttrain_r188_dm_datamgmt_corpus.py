#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r188_dm_datamgmt_corpus.py
R188 -- v18 PyAether SFT corpus: the dm* "data-management object" blind spot.

BACKGROUND (R181 coverage audit, updated R188):
  v11-v17 (343 pairs) cover 57/164 eval raw pyScript APIs. 107 remain blind.
  The blind set's highest single-API blind is dmGetObj (eval_usage=8).
  The dm* data-management family is:
    dmGetObj        : eval_count=8   (overloaded: lib -> cell -> view objects)
    dmGetObjF       : eval_count=1   (overloaded: file objects, wildcard support)
    dmGetObjType    : eval_count=1   (returns type string for any dm object)
    dmGetObjReadPath: eval_count=1   (returns read path for any dm object)
    dmDeleteObj     : eval_count=1   (permanently delete a dm object)
  Total: 5 APIs, 12 eval usages. All ISOLATE-class (eval_count>0, appear as
  helpers in eval solutions). The red line (S5.1) isolates on eval *entry_point*
  strings (the 155 task function names), NOT on helper API names. Teaching the
  *public API reference* of these primitives is explicitly allowed. The
  fingerprint scan below rejects any pair whose prompt+completion contains a
  literal eval entry_point string.

  Authoritative signatures fetched via pyAether MCP get_api_details (R188 wake).

v18: 5 dm* data-management APIs with S1 doc->code, S4 multi-step trace, S5 param
  variation, S3 multi-API chains (query -> inspect -> path -> delete lifecycle),
  S6 API lookup. Strict pollution scan against all 155 eval entry_points.

Usage:
  python3 baize_posttrain_r188_dm_datamgmt_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v18_dm_datamgmt.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

# All 5 are ISOLATE (eval_count>0, appear as helpers in eval solutions).
# Signatures from pyAether MCP get_api_details (authoritative).
API_DOCS = {}

API_DOCS["dmGetObj"] = {
    "sig": 'dmGetObj(libName: emyString, [cellName: emyString, [viewName: emyString]]) -> dmLibObj | dmCellObj | dmViewObj',
    "desc": "Get a data-management object for a library, cell, or view. Overloaded by argument count: 1 arg returns dmLibObj, 2 args return dmCellObj, 3 args return dmViewObj. Returns None if the specified object does not exist.",
    "params": {
        "libName": "emyString - library name",
        "cellName": "emyString, optional - cell name within the library",
        "viewName": "emyString, optional - view name within the cell",
    },
    "returns": "dmLibObj (1 arg) | dmCellObj (2 args) | dmViewObj (3 args) | None on failure",
    "attrs_lib": "name, type, readPath, writePath, owner, group, ownerAccess, groupAccess, lastModify, isReadable, isWriteable, cells, files",
    "attrs_cell": "name, type, readPath, writePath, owner, group, ownerAccess, groupAccess, lastModify, isReadable, isWriteable, views, files",
    "attrs_view": "name, type, readPath, writePath, owner, group, ownerAccess, groupAccess, lastModify, isReadable, isWriteable, lib, cell, files",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.dmGetObj("my_lib")\n'
                '>>> cell = pyScript.dmGetObj("my_lib", "inv")\n'
                '>>> view = pyScript.dmGetObj("my_lib", "inv", "layout")'),
    "category": "Dm Commands / Data Management",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "Overloaded by arg count (1/2/3). Returns None (not 0) on failure -- check with 'is not None'. Access .cells/.views/.files to traverse the hierarchy."}

API_DOCS["dmGetObjF"] = {
    "sig": 'dmGetObjF(libName: emyString, [cellName: emyString, [viewName: emyString,]] fileName: emyString) -> dmLibFileObj | dmCellFileObj | dmViewFileObj',
    "desc": "Get a data-management file object. Overloaded by argument count (2/3/4 args). Supports wildcards: fileName='*' finds any file; fileName='*.ext' finds files ending in .ext.",
    "params": {
        "libName": "emyString - library name",
        "cellName": "emyString, optional - cell name",
        "viewName": "emyString, optional - view name",
        "fileName": "emyString - file name; '*' matches any, '*.ext' matches by suffix",
    },
    "returns": "dmLibFileObj (2 args) | dmCellFileObj (3 args) | dmViewFileObj (4 args) | None on failure",
    "attrs": "name, type, readPath, writePath, lastModify, owner, ownerAccess, group, groupAccess, publicAccess, isReadable, isWriteable, lib, cell, view",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> f = pyScript.dmGetObjF("my_lib", "tech.db")\n'
                '>>> f2 = pyScript.dmGetObjF("my_lib", "inv", "data.dm")\n'
                '>>> f3 = pyScript.dmGetObjF("my_lib", "inv", "layout", "layout.oa")'),
    "category": "Dm Commands / Data Management",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Overloaded by arg count (2/3/4). Wildcard: '*' lists files in master.tag; '*.ext' matches by suffix. Use for file-level inspection of design data."}

API_DOCS["dmGetObjType"] = {
    "sig": 'dmGetObjType(obj: dmLibObj | dmCellObj | dmViewObj | dmLibFileObj | dmCellFileObj | dmViewFileObj) -> emyString',
    "desc": "Return the type string of a data-management object. Accepts any dm object returned by dmGetObj or dmGetObjF. Returns an empty string for None input.",
    "params": {"obj": "dmLibObj | dmCellObj | dmViewObj | dmLibFileObj | dmCellFileObj | dmViewFileObj - the dm object to inspect"},
    "returns": "emyString - type string (e.g. 'libType', 'cellType', 'viewType', 'libFileType', 'cellFileType', 'viewFileType')",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.dmGetObj("my_lib")\n'
                '>>> pyScript.dmGetObjType(lib)\n'
                "emyString('libType')"),
    "category": "Dm Commands / Data Management",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Overloaded for all 6 dm object types. Returns type string via str(). Returns empty string for None -- always check result is not None first."}

API_DOCS["dmGetObjReadPath"] = {
    "sig": 'dmGetObjReadPath(obj: dmLibObj | dmCellObj | dmViewObj | dmLibFileObj | dmCellFileObj | dmViewFileObj) -> emyString',
    "desc": "Return the physical read path of a data-management object. Overloaded for all 6 dm object types. Returns empty string for virtual (in-memory) objects.",
    "params": {"obj": "dmLibObj | dmCellObj | dmViewObj | dmLibFileObj | dmCellFileObj | dmViewFileObj - the dm object"},
    "returns": "emyString - the read path on disk; empty string if the object is virtual or has no physical storage",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.dmGetObj("my_lib")\n'
                '>>> path = pyScript.dmGetObjReadPath(lib)\n'
                '>>> print(str(path))'),
    "category": "Dm Commands / Data Management",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Lightweight -- returns cached attribute, no filesystem access. Returns empty string for virtual objects. Use str() to convert to Python string. Pairs with dmGetObj/dmGetObjF."}

API_DOCS["dmDeleteObj"] = {
    "sig": 'dmDeleteObj(obj: dmLibObj | dmCellObj | dmViewObj | dmLibFileObj | dmCellFileObj | dmViewFileObj) -> bool',
    "desc": "Permanently delete a data-management object. Accepts any dm object. Returns True on success, False on failure. Deleting a parent (e.g. library) cascades to children.",
    "params": {"obj": "dmLibObj | dmCellObj | dmViewObj | dmLibFileObj | dmCellFileObj | dmViewFileObj - the dm object to delete"},
    "returns": "bool - True if deleted, False on failure",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.dmGetObj("temp_lib")\n'
                '>>> if lib is not None:\n'
                '...     pyScript.dmDeleteObj(lib)'),
    "category": "Dm Commands / Data Management",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Permanent deletion -- cannot be undone. Deleting a library cascades to its cells/views/files. Always verify the object exists (dmGetObj returns non-None) before deleting. Check return value."}

API_ORDER = ["dmGetObj", "dmGetObjF", "dmGetObjType", "dmGetObjReadPath", "dmDeleteObj"]


def load_eval_entry_points():
    """Load all entry_point strings from the 158-task eval dataset for the
    fingerprint contamination scan. The task bodies themselves are NOT read."""
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
    """Return first eval entry_point substring found in text, else None."""
    for ep in eval_eps:
        if ep and ep in text:
            return ep
    return None


def _doc_block(name):
    """Format a focused API reference block for the S1 prompt."""
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
        _add("S1", "v18-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S4: multi-step trace (5 pairs, one per API) ----
    s4_traces = [
        ("dmGetObj",
         "Query a library named 'analog_lib', then list its cell names and check if the library is writable.",
         ["dmGetObj"],
         ("import pyAether as pyScript\n\n"
          "# Step 1: get the library object\n"
          'lib = pyScript.dmGetObj("analog_lib")\n'
          "if lib is None:\n"
          '    raise RuntimeError("Library not found")\n\n'
          "# Step 2: list cell names\n"
          "cell_names = [c.name for c in lib.cells]\n"
          'print("Cells:", cell_names)\n\n'
          "# Step 3: check writability\n"
          'print("Is writable:", lib.isWriteable)')),
        ("dmGetObjF",
         "Find the technology file 'tech.db' in library 'std_cell_lib', then retrieve its physical read path.",
         ["dmGetObjF", "dmGetObjReadPath"],
         ("import pyAether as pyScript\n\n"
          "# Step 1: get the file object\n"
          'fobj = pyScript.dmGetObjF("std_cell_lib", "tech.db")\n'
          "if fobj is None:\n"
          '    raise RuntimeError("File not found")\n\n'
          "# Step 2: get the physical read path\n"
          "path = pyScript.dmGetObjReadPath(fobj)\n"
          'print("Read path:", str(path))')),
        ("dmGetObjType",
         "Given a dm object obtained from dmGetObj with three arguments, determine its type and branch logic accordingly.",
         ["dmGetObj", "dmGetObjType"],
         ("import pyAether as pyScript\n\n"
          '# Step 1: get the view object (3 args)\n'
          'obj = pyScript.dmGetObj("my_lib", "inv", "layout")\n'
          "if obj is None:\n"
          '    raise RuntimeError("View not found")\n\n'
          "# Step 2: determine the type\n"
          "obj_type = str(pyScript.dmGetObjType(obj))\n"
          'print("Object type:", obj_type)\n\n'
          "# Step 3: branch on type\n"
          'if obj_type == "viewType":\n'
          '    print("This is a view object")\n'
          "else:\n"
          '    print("Unexpected type:", obj_type)')),
        ("dmGetObjReadPath",
         "Retrieve the read paths of all cells in a library and filter out those with empty paths (virtual objects).",
         ["dmGetObj", "dmGetObjReadPath"],
         ("import pyAether as pyScript\n\n"
          '# Step 1: get the library object\n'
          'lib = pyScript.dmGetObj("io_lib")\n'
          "if lib is None:\n"
          '    raise RuntimeError("Library not found")\n\n'
          "# Step 2: iterate cells and get read paths\n"
          "real_paths = []\n"
          "for cell in lib.cells:\n"
          '    cell_obj = pyScript.dmGetObj("io_lib", cell.name)\n'
          "    if cell_obj is not None:\n"
          "        p = str(pyScript.dmGetObjReadPath(cell_obj))\n"
          "        if p:\n"
          "            real_paths.append((cell.name, p))\n\n"
          'print("Cells with physical paths:", len(real_paths))')),
        ("dmDeleteObj",
         "Safely delete a temporary library 'tmp_work_lib' if it exists, verifying deletion afterward.",
         ["dmGetObj", "dmDeleteObj"],
         ("import pyAether as pyScript\n\n"
          "# Step 1: check if the library exists\n"
          'lib = pyScript.dmGetObj("tmp_work_lib")\n'
          "if lib is None:\n"
          '    print("Library does not exist, nothing to delete")\n'
          "else:\n"
          "    # Step 2: delete it\n"
          "    result = pyScript.dmDeleteObj(lib)\n"
          '    print("Delete result:", result)\n'
          "    # Step 3: verify deletion\n"
          '    check = pyScript.dmGetObj("tmp_work_lib")\n'
          "    if check is None:\n"
          '        print("Confirmed: library deleted")\n'
          "    else:\n"
          '        print("Warning: library still exists")')),
    ]
    for api, prompt_text, api_used, completion in s4_traces:
        prompt = ("You are an EDA automation engineer. %s "
                  "Use the PyAether API correctly, with proper error handling." % prompt_text)
        _add("S4", "v18-S4-%s" % api, prompt, completion, api_used,
             "S4 multi_step trace for %s" % api)

    # ---- S5: parameter variation (5 pairs, one per API) ----
    s5_variants = [
        ("dmGetObj",
         "Show three different ways to call dmGetObj: with 1 arg, 2 args, and 3 args, explaining what each returns.",
         ["dmGetObj"],
         ("import pyAether as pyScript\n\n"
          "# 1 arg: returns dmLibObj (library object)\n"
          'lib_obj = pyScript.dmGetObj("ref_lib")\n'
          'print("Library:", lib_obj.name if lib_obj else "not found")\n\n'
          "# 2 args: returns dmCellObj (cell object)\n"
          'cell_obj = pyScript.dmGetObj("ref_lib", "nand2")\n'
          'print("Cell:", cell_obj.name if cell_obj else "not found")\n\n'
          "# 3 args: returns dmViewObj (view object)\n"
          'view_obj = pyScript.dmGetObj("ref_lib", "nand2", "schematic")\n'
          'print("View:", view_obj.name if view_obj else "not found")')),
        ("dmGetObjF",
         "Show three overloads of dmGetObjF: library-level file, cell-level file, and view-level file with a wildcard.",
         ["dmGetObjF"],
         ("import pyAether as pyScript\n\n"
          "# 2 args: library-level file\n"
          'lib_file = pyScript.dmGetObjF("tech_lib", "tech.db")\n'
          'print("Lib file:", lib_file.name if lib_file else "not found")\n\n'
          "# 3 args: cell-level file\n"
          'cell_file = pyScript.dmGetObjF("tech_lib", "inv", "data.dm")\n'
          'print("Cell file:", cell_file.name if cell_file else "not found")\n\n'
          "# 4 args with wildcard: view-level file matching *.oa\n"
          'view_file = pyScript.dmGetObjF("tech_lib", "inv", "layout", "*.oa")\n'
          'print("View file:", view_file.name if view_file else "not found")')),
        ("dmGetObjType",
         "Show how dmGetObjType works on different object types: a library, a cell, and a file object.",
         ["dmGetObj", "dmGetObjF", "dmGetObjType"],
         ("import pyAether as pyScript\n\n"
          "# Type of a library object\n"
          'lib = pyScript.dmGetObj("demo_lib")\n'
          'print("Lib type:", str(pyScript.dmGetObjType(lib)))\n\n'
          "# Type of a cell object\n"
          'cell = pyScript.dmGetObj("demo_lib", "buf")\n'
          'print("Cell type:", str(pyScript.dmGetObjType(cell)))\n\n'
          "# Type of a file object\n"
          'fobj = pyScript.dmGetObjF("demo_lib", "tech.db")\n'
          'print("File type:", str(pyScript.dmGetObjType(fobj)))')),
        ("dmGetObjReadPath",
         "Show how dmGetObjReadPath returns paths for a library, a cell, and a view object, and how to handle empty paths.",
         ["dmGetObj", "dmGetObjReadPath"],
         ("import pyAether as pyScript\n\n"
          '# Library read path\n'
          'lib = pyScript.dmGetObj("my_lib")\n'
          'lib_path = str(pyScript.dmGetObjReadPath(lib))\n'
          'print("Lib path:", lib_path or "(virtual)")\n\n'
          '# Cell read path\n'
          'cell = pyScript.dmGetObj("my_lib", "mux2")\n'
          'cell_path = str(pyScript.dmGetObjReadPath(cell))\n'
          'print("Cell path:", cell_path or "(virtual)")\n\n'
          '# View read path\n'
          'view = pyScript.dmGetObj("my_lib", "mux2", "layout")\n'
          'view_path = str(pyScript.dmGetObjReadPath(view))\n'
          'print("View path:", view_path or "(virtual)")')),
        ("dmDeleteObj",
         "Show safe deletion patterns: delete a cell, delete a view, and delete a file object, each with existence check and result check.",
         ["dmGetObj", "dmGetObjF", "dmDeleteObj"],
         ("import pyAether as pyScript\n\n"
          '# Delete a cell\n'
          'cell = pyScript.dmGetObj("work_lib", "old_cell")\n'
          'if cell is not None:\n'
          '    ok = pyScript.dmDeleteObj(cell)\n'
          '    print("Cell deleted:", ok)\n\n'
          '# Delete a view\n'
          'view = pyScript.dmGetObj("work_lib", "old_cell", "schematic")\n'
          'if view is not None:\n'
          '    ok = pyScript.dmDeleteObj(view)\n'
          '    print("View deleted:", ok)\n\n'
          '# Delete a file\n'
          'fobj = pyScript.dmGetObjF("work_lib", "temp.log")\n'
          'if fobj is not None:\n'
          '    ok = pyScript.dmDeleteObj(fobj)\n'
          '    print("File deleted:", ok)')),
    ]
    for api, prompt_text, api_used, completion in s5_variants:
        prompt = ("You are an EDA automation engineer. %s "
                  "Use the PyAether API correctly with clear comments." % prompt_text)
        _add("S5", "v18-S5-%s" % api, prompt, completion, api_used,
             "S5 param_variation for %s" % api)

    # ---- S3: multi-API chains (5 pairs) ----
    chains = [
        ("v18-S3-chain1",
         "Build a complete data-management inspection routine: list all libraries, pick the first one, iterate its cells, and for each cell print its type and read path.",
         ["dmGetObj", "dmGetObjType", "dmGetObjReadPath"],
         ("import pyAether as pyScript\n\n"
          "# Discover libraries\n"
          'lib_names = [str(l) for l in pyScript.dbGetAllLibs()]\n'
          'if not lib_names:\n'
          '    print("No libraries found")\n'
          "else:\n"
          '    lib = pyScript.dmGetObj(lib_names[0])\n'
          "    for cell in lib.cells:\n"
          '        cell_obj = pyScript.dmGetObj(lib_names[0], cell.name)\n'
          "        if cell_obj is not None:\n"
          '            t = str(pyScript.dmGetObjType(cell_obj))\n'
          '            p = str(pyScript.dmGetObjReadPath(cell_obj))\n'
          '            print("%s [%s] -> %s" % (cell.name, t, p or "(virtual)"))')),
        ("v18-S3-chain2",
         "Find a file in a view using a wildcard, get its read path, then determine its type.",
         ["dmGetObjF", "dmGetObjReadPath", "dmGetObjType"],
         ("import pyAether as pyScript\n\n"
          '# Wildcard search for any file in a view\n'
          'fobj = pyScript.dmGetObjF("design_lib", "top", "layout", "*")\n'
          "if fobj is not None:\n"
          '    path = str(pyScript.dmGetObjReadPath(fobj))\n'
          '    ftype = str(pyScript.dmGetObjType(fobj))\n'
          '    print("File: %s, Type: %s, Path: %s" % (fobj.name, ftype, path))\n'
          "else:\n"
          '    print("No file found")')),
        ("v18-S3-chain3",
         "Create a safe cleanup routine: get a library, check if it is writable, and if so delete it after confirming.",
         ["dmGetObj", "dmDeleteObj"],
         ("import pyAether as pyScript\n\n"
          'def safe_cleanup(lib_name, confirmed=False):\n'
          '    lib = pyScript.dmGetObj(lib_name)\n'
          "    if lib is None:\n"
          '        return False, "library not found"\n'
          "    if not lib.isWriteable:\n"
          '        return False, "library is read-only"\n'
          "    if not confirmed:\n"
          '        return False, "deletion not confirmed"\n'
          "    result = pyScript.dmDeleteObj(lib)\n"
          '    return result, "deleted" if result else "delete failed"\n\n'
          'ok, msg = safe_cleanup("scratch_lib", confirmed=True)\n'
          'print("Cleanup:", msg)')),
        ("v18-S3-chain4",
         "Inspect a library hierarchy: get the library, list cells, for each cell get its views, and report the type of each view object.",
         ["dmGetObj", "dmGetObjType"],
         ("import pyAether as pyScript\n\n"
          'lib = pyScript.dmGetObj("tech_lib")\n'
          "if lib is None:\n"
          '    print("Library not found")\n'
          "else:\n"
          "    for cell in lib.cells:\n"
          '        cell_obj = pyScript.dmGetObj("tech_lib", cell.name)\n'
          "        if cell_obj is None:\n"
          "            continue\n"
          "        for view in cell_obj.views:\n"
          '            vobj = pyScript.dmGetObj("tech_lib", cell.name, view.name)\n'
          "            if vobj is not None:\n"
          '                vt = str(pyScript.dmGetObjType(vobj))\n'
          '                print("  %s/%s/%s [%s]" % (lib.name, cell.name, view.name, vt))')),
        ("v18-S3-chain5",
         "Build a file inventory: for a given library, use dmGetObjF with wildcard to find all files, then report each file type and path.",
         ["dmGetObjF", "dmGetObjType", "dmGetObjReadPath"],
         ("import pyAether as pyScript\n\n"
          'def inventory_lib_files(lib_name):\n'
          '    results = []\n'
          '    fobj = pyScript.dmGetObjF(lib_name, "*")\n'
          "    if fobj is not None:\n"
          '        ftype = str(pyScript.dmGetObjType(fobj))\n'
          '        fpath = str(pyScript.dmGetObjReadPath(fobj))\n'
          '        results.append((fobj.name, ftype, fpath))\n'
          "    return results\n\n"
          'files = inventory_lib_files("my_lib")\n'
          'for name, ftype, fpath in files:\n'
          '    print("  %s [%s] -> %s" % (name, ftype, fpath or "(virtual)"))')),
    ]
    for cid, prompt, api_used, completion in chains:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")

    # ---- S6: API lookup (5 pairs) ----
    lookups = [
        ("get a data-management object for a library or cell or view", "dmGetObj",
         'lib = pyScript.dmGetObj("my_lib")'),
        ("get a data-management file object with optional wildcards", "dmGetObjF",
         'fobj = pyScript.dmGetObjF("my_lib", "tech.db")'),
        ("determine the type of a data-management object", "dmGetObjType",
         't = str(pyScript.dmGetObjType(lib))'),
        ("get the physical read path of a data-management object", "dmGetObjReadPath",
         'path = str(pyScript.dmGetObjReadPath(lib))'),
        ("permanently delete a data-management object", "dmDeleteObj",
         'result = pyScript.dmDeleteObj(lib)'),
    ]
    for intent, api, usage in lookups:
        prompt = ("You are an EDA automation assistant. Which PyAether API is "
                  "used to %s? Show a minimal correct usage example." % intent)
        completion = ("The API is `%s`.\n\n```python\nimport pyAether as "
                      "pyScript\n%s\n```" % (api, usage))
        _add("S6", "v18-S6-%s" % api, prompt, completion, [api],
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
        "report_id": "R188",
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
        sys.stderr.write("GATE: FAIL (pollution detected) -- do NOT use v18\n")
        sys.exit(2)
    sys.stderr.write("GATE: PASS -- v18 is training-ready\n")


if __name__ == "__main__":
    main()
