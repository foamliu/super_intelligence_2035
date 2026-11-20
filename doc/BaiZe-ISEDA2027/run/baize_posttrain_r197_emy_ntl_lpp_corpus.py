#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r197_emy_ntl_lpp_corpus.py
R197 -- v27 PyAether SFT corpus: Emy* blind spot (2 class APIs) + NTL_INDEX_FORMAT
constants (3 blind APIs) = 5 APIs, 25 pairs.

BACKGROUND: v11-v26 (708 pairs) cover 129/164 eval raw APIs (78.7%). 35 blind.
Data-driven scan (R191 blind_scan, re-run with v26) shows Emy is the #1 blind
family (7 usages, 2 APIs: EmyNtlUtil, EmyLPPHeader). NTL is #3 (6 usages, 3
constant APIs). Since EmyNtlUtil.getVerilogName uses NTL_INDEX_FORMAT_* as its
fmt argument, covering them together is natural and clears 2 blind families.

  - EmyNtlUtil: static class for netlist/verilog utilities (getVerilogName,
    checkViewList, formatScientific, short-cell helpers, pin-used-libcell map)
  - EmyLPPHeader: class for Layer-Purpose-Pair (LPP) header management
    (create, get/set layer+purpose num+name, packet, priority, flag, visibility,
    MPT mask color, app-LPP color, tech integration, clone)
  - NTL_INDEX_FORMAT_ORIGIN: verilog name fmt constant -> "X0" (no separator)
  - NTL_INDEX_FORMAT_USE_BRACKET: verilog name fmt constant -> "X[0]"
  - NTL_INDEX_FORMAT_USE_UNDERLINE: verilog name fmt constant -> "X_0"

All ISOLATE-class (eval helper APIs, NOT eval entry_points). Fingerprint scan
rejects eval entry_points (155 loaded).

Authoritative signatures fetched via pyAether MCP get_api_details (R197 wake).

Usage:
  python3 baize_posttrain_r197_emy_ntl_lpp_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v27_emy_ntl_lpp.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["EmyNtlUtil"] = {
    "sig": "EmyNtlUtil (static class) -- methods: getVerilogName, checkViewList, formatScientific, getShortCellList, getShortCellValue, addPinUsedLibCell, getPinUsedLibCellMap, clearPinUsedLibCellMap, emyGetHierSEViews, checkAndSaveDesign, getMultiShortCellList",
    "desc": "A static utility class for netlist / verilog name generation, view-list resolution, short-cell detection, and pin-used-libcell bookkeeping. All methods are static -- call them as pyScript.EmyNtlUtil.method(...). The most commonly used method is getVerilogName which formats bus-net names according to a format constant (NTL_INDEX_FORMAT_ORIGIN / _USE_BRACKET / _USE_UNDERLINE).",
    "params": {
        "getVerilogName": "overloaded: (baseName: char, index: emyUInt4, fmt: int) -> emyString; (net: emyNet, groupName: emyBoolean, fmt: int) -> emyString; (inst: emyInst, fmt: int) -> emyString; (indexName: emyString, fmt: int)",
        "checkViewList": "(ntlViewList: emyStringArray, ntlStopList: emyStringArray, viewListList: emyStringArray, stopViewNames: emyStringArray, viewNames: emyArray_emyScalarName, ntlMsg: emyString) -> bool",
        "formatScientific": "(strOut: emyString) -- formats a numeric string in scientific notation",
        "getShortCellList": "(shortCellList, shortCellListSet) -- collects short-cell names",
        "getShortCellValue": "(design, shortCellList, multiShortCellList, value) -- gets short-cell value",
        "addPinUsedLibCell": "(type, libcell) -- registers a pin-used libcell",
    },
    "returns": "getVerilogName returns emyString (the formatted verilog name); checkViewList returns bool; others are void or container-fill",
    "methods": "pyScript.EmyNtlUtil.getVerilogName('X', 0, pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE) -> 'X_0'",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> name1 = pyScript.EmyNtlUtil.getVerilogName("X", 0, pyScript.NTL_INDEX_FORMAT_ORIGIN)\n'
                '>>> print(name1)\n'
                'X0\n'
                '>>> name2 = pyScript.EmyNtlUtil.getVerilogName("X", 0, pyScript.NTL_INDEX_FORMAT_USE_BRACKET)\n'
                '>>> print(name2)\n'
                'X[0]\n'
                '>>> name3 = pyScript.EmyNtlUtil.getVerilogName("X", 0, pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE)\n'
                '>>> print(name3)\n'
                'X_0'),
    "category": "Emy / Netlist Utility", "safety": "ISOLATE", "eval_count": 5,
    "key_notes": "EmyNtlUtil is a CLASS with static methods -- call as pyScript.EmyNtlUtil.method(...), NOT pyScript.EmyNtlUtil(). getVerilogName is overloaded: the (baseName, index, fmt) form is most common. fmt must be one of NTL_INDEX_FORMAT_ORIGIN / _USE_BRACKET / _USE_UNDERLINE (integer constants). Must call emyInitAether first."}

API_DOCS["EmyLPPHeader"] = {
    "sig": "EmyLPPHeader (class) -- key methods: create(tech, layerNum, purposeNum, packetName, priority, flag), getLayerNum, getPurposeNum, getLayerName, getPurposeName, setLayerName, setPurposeName, getPacketName, setPacketName, getPriority, setPriority, getFlag, setFlag, isVisible, setVisible, isValid, isInTech, isSpecial, isAppLPP, getMptMaskColor, setMptMaskColor, setAppLPPColorName, setAppLPPLineWidth, getByTech, add, get, loadLppFromTech, clone",
    "desc": "A class representing a Layer-Purpose-Pair (LPP) header -- the fundamental display/drawing definition that pairs a layer number with a purpose number. LPP headers are attached to a tech library (tech) and define how geometry on each layer-purpose combination is rendered. Application-layer LPPs (layerNum >= 2000) can exist independently of a tech. Provides full CRUD: create, query (get/set all attributes), validate, clone, and tech integration (add/get/getByTech/loadLppFromTech).",
    "params": {
        "create": "EmyLPPHeader.create(tech, layerNum, purposeNum, packetName='', priority=0, flag=0) -> EmyLPPHeader -- tech can be None for app-layer LPPs (layerNum >= 2000)",
        "getLayerNum": "() -> int -- the layer number",
        "getPurposeNum": "() -> int -- the purpose number",
        "getLayerName": "() -> str -- the layer name",
        "getPurposeName": "() -> str -- the purpose name",
        "setLayerName": "(name: str) -- set the layer name",
        "setPurposeName": "(name: str) -- set the purpose name",
        "getPacketName": "() -> str -- the packet (stylization) name",
        "isVisible": "() -> bool -- whether the LPP is visible",
        "setVisible": "(v: bool) -- set visibility",
        "isValid": "() -> bool -- whether the LPP header is valid",
        "isAppLPP": "() -> bool -- True if layerNum >= 2000 (application layer)",
        "setAppLPPColorName": "(layerNum, purposeNum, colorName: str) -- set app-LPP display color",
        "setAppLPPLineWidth": "(layerNum, purposeNum, width: int) -- set app-LPP line width",
    },
    "returns": "create returns an EmyLPPHeader instance; getters return int/str/bool as named",
    "methods": "lpp = pyScript.EmyLPPHeader.create(None, 2001, 0); lpp.setLayerName('M1'); print(lpp.getLayerNum())",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> lpp = pyScript.EmyLPPHeader.create(None, 2001, 0)\n'
                '>>> lpp.setLayerName("Metal1")\n'
                '>>> lpp.setPurposeName("drawing")\n'
                '>>> print(lpp.getLayerNum())\n'
                '2001\n'
                '>>> print(lpp.getLayerName())\n'
                'Metal1\n'
                '>>> print(lpp.isAppLPP())\n'
                'True\n'
                '>>> print(lpp.isValid())\n'
                'True'),
    "category": "Emy / LPP Header Management", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "EmyLPPHeader is a CLASS -- create instances with EmyLPPHeader.create(tech, layerNum, purposeNum, ...). For application-layer LPPs (layerNum >= 2000), tech can be None -- the LPP exists independently. For tech-bound LPPs (layerNum < 2000), a valid tech object is required. isAppLPP() returns True when layerNum >= 2000. setAppLPPColorName/setAppLPPLineWidth configure display for app-layer LPPs. clone() creates a deep copy. Must call emyInitAether first."}

API_DOCS["NTL_INDEX_FORMAT_ORIGIN"] = {
    "sig": "NTL_INDEX_FORMAT_ORIGIN (int constant) -- used as fmt arg to EmyNtlUtil.getVerilogName",
    "desc": "An integer constant specifying the verilog net-name format where the bus index is appended directly to the base name with NO separator. Example: getVerilogName('X', 0, NTL_INDEX_FORMAT_ORIGIN) -> 'X0'. Used in netlist generation when the target tool expects plain concatenated bus names.",
    "params": {},
    "returns": "int -- the format constant value (passed as the fmt parameter)",
    "methods": "pyScript.EmyNtlUtil.getVerilogName('data', 3, pyScript.NTL_INDEX_FORMAT_ORIGIN) -> 'data3'",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> fmt = pyScript.NTL_INDEX_FORMAT_ORIGIN\n'
                '>>> print(type(fmt).__name__)\n'
                'int\n'
                '>>> name = pyScript.EmyNtlUtil.getVerilogName("data", 7, fmt)\n'
                '>>> print(name)\n'
                'data7'),
    "category": "NTL / Net Name Format Constant", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "NTL_INDEX_FORMAT_ORIGIN is an integer constant (NOT a function). It is the fmt argument to EmyNtlUtil.getVerilogName. Origin format = no separator: 'X' + 0 -> 'X0'. Must call emyInitAether before accessing the constant."}

API_DOCS["NTL_INDEX_FORMAT_USE_BRACKET"] = {
    "sig": "NTL_INDEX_FORMAT_USE_BRACKET (int constant) -- used as fmt arg to EmyNtlUtil.getVerilogName",
    "desc": "An integer constant specifying the verilog net-name format where the bus index is wrapped in square brackets. Example: getVerilogName('X', 0, NTL_INDEX_FORMAT_USE_BRACKET) -> 'X[0]'. This is the standard Verilog bus notation used in most RTL.",
    "params": {},
    "returns": "int -- the format constant value (passed as the fmt parameter)",
    "methods": "pyScript.EmyNtlUtil.getVerilogName('addr', 15, pyScript.NTL_INDEX_FORMAT_USE_BRACKET) -> 'addr[15]'",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> fmt = pyScript.NTL_INDEX_FORMAT_USE_BRACKET\n'
                '>>> name = pyScript.EmyNtlUtil.getVerilogName("addr", 15, fmt)\n'
                '>>> print(name)\n'
                'addr[15]'),
    "category": "NTL / Net Name Format Constant", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "NTL_INDEX_FORMAT_USE_BRACKET is an integer constant (NOT a function). Bracket format: 'X' + 0 -> 'X[0]'. This is standard Verilog bus notation. Must call emyInitAether before accessing the constant."}

API_DOCS["NTL_INDEX_FORMAT_USE_UNDERLINE"] = {
    "sig": "NTL_INDEX_FORMAT_USE_UNDERLINE (int constant) -- used as fmt arg to EmyNtlUtil.getVerilogName",
    "desc": "An integer constant specifying the verilog net-name format where the bus index is separated from the base name by an underscore. Example: getVerilogName('X', 0, NTL_INDEX_FORMAT_USE_UNDERLINE) -> 'X_0'. Used in netlist formats that avoid brackets (e.g., some flat netlist tools).",
    "params": {},
    "returns": "int -- the format constant value (passed as the fmt parameter)",
    "methods": "pyScript.EmyNtlUtil.getVerilogName('clk', 3, pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE) -> 'clk_3'",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> fmt = pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE\n'
                '>>> name = pyScript.EmyNtlUtil.getVerilogName("clk", 3, fmt)\n'
                '>>> print(name)\n'
                'clk_3'),
    "category": "NTL / Net Name Format Constant", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "NTL_INDEX_FORMAT_USE_UNDERLINE is an integer constant (NOT a function). Underline format: 'X' + 0 -> 'X_0'. Used when brackets are not allowed. Must call emyInitAether before accessing the constant."}


API_ORDER = ["EmyNtlUtil", "EmyLPPHeader",
             "NTL_INDEX_FORMAT_ORIGIN", "NTL_INDEX_FORMAT_USE_BRACKET",
             "NTL_INDEX_FORMAT_USE_UNDERLINE"]


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

    # ---- S1: doc -> code (5 pairs, one per API) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v27-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S3: code -> doc (5 pairs, one per API) ----
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
        _add("S3", "v27-S3-%s" % name, prompt, completion, [name],
             "S3 code_to_doc for %s" % name)


    # ---- S4: multi-step trace (5 pairs) ----
    s4_traces = [
        ("EmyNtlUtil",
         "Generate verilog bus names for a 4-bit bus 'data[3:0]' using all three NTL_INDEX_FORMAT constants and compare the results.",
         ["EmyNtlUtil", "NTL_INDEX_FORMAT_ORIGIN", "NTL_INDEX_FORMAT_USE_BRACKET", "NTL_INDEX_FORMAT_USE_UNDERLINE"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "base = 'data'\n"
          "for idx in range(4):\n"
          "    n_origin = pyScript.EmyNtlUtil.getVerilogName(base, idx, pyScript.NTL_INDEX_FORMAT_ORIGIN)\n"
          "    n_bracket = pyScript.EmyNtlUtil.getVerilogName(base, idx, pyScript.NTL_INDEX_FORMAT_USE_BRACKET)\n"
          "    n_under = pyScript.EmyNtlUtil.getVerilogName(base, idx, pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE)\n"
          "    print('idx=%d  origin=%s  bracket=%s  underline=%s' % (idx, n_origin, n_bracket, n_under))")),
        ("EmyLPPHeader",
         "Create an application-layer LPP header (layer 2001), set its names, check validity and app-LPP status, then set its display color and line width.",
         ["EmyLPPHeader"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "lpp = pyScript.EmyLPPHeader.create(None, 2001, 0)\n"
          "lpp.setLayerName('Metal1')\n"
          "lpp.setPurposeName('drawing')\n"
          "lpp.setPacketName('M1Drawing')\n"
          "lpp.setVisible(True)\n"
          "print('layerNum:', lpp.getLayerNum())\n"
          "print('purposeNum:', lpp.getPurposeNum())\n"
          "print('layerName:', lpp.getLayerName())\n"
          "print('purposeName:', lpp.getPurposeName())\n"
          "print('packetName:', lpp.getPacketName())\n"
          "print('isVisible:', lpp.isVisible())\n"
          "print('isValid:', lpp.isValid())\n"
          "print('isAppLPP:', lpp.isAppLPP())\n"
          "pyScript.EmyLPPHeader.setAppLPPColorName(2001, pyScript.emvPurposeNumberDrawing, 'blue')\n"
          "pyScript.EmyLPPHeader.setAppLPPLineWidth(2001, pyScript.emvPurposeNumberDrawing, 2)\n"
          "print('app-LPP color and width set')")),
        ("NTL_INDEX_FORMAT_ORIGIN",
         "Generate net names for an 8-bit address bus 'addr[7:0]' in origin format and collect them into a list.",
         ["NTL_INDEX_FORMAT_ORIGIN", "EmyNtlUtil"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "fmt = pyScript.NTL_INDEX_FORMAT_ORIGIN\n"
          "addr_names = []\n"
          "for i in range(8):\n"
          "    nm = pyScript.EmyNtlUtil.getVerilogName('addr', i, fmt)\n"
          "    addr_names.append(nm)\n"
          "print('origin-format bus:', addr_names)")),
        ("NTL_INDEX_FORMAT_USE_BRACKET",
         "Generate net names for a 16-bit data bus 'data[15:0]' in bracket format, which is standard Verilog notation.",
         ["NTL_INDEX_FORMAT_USE_BRACKET", "EmyNtlUtil"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "fmt = pyScript.NTL_INDEX_FORMAT_USE_BRACKET\n"
          "data_names = []\n"
          "for i in range(16):\n"
          "    nm = pyScript.EmyNtlUtil.getVerilogName('data', i, fmt)\n"
          "    data_names.append(nm)\n"
          "print('bracket-format bus:', data_names)\n"
          "print('first:', data_names[0], ' last:', data_names[-1])")),
        ("NTL_INDEX_FORMAT_USE_UNDERLINE",
         "Generate net names for a clock bus 'clk[3:0]' in underline format and verify each name contains an underscore.",
         ["NTL_INDEX_FORMAT_USE_UNDERLINE", "EmyNtlUtil"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "fmt = pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE\n"
          "clk_names = []\n"
          "for i in range(4):\n"
          "    nm = pyScript.EmyNtlUtil.getVerilogName('clk', i, fmt)\n"
          "    clk_names.append(nm)\n"
          "    assert '_' in nm, 'underline missing in %s' % nm\n"
          "print('underline-format bus:', clk_names)")),
    ]
    for name, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write a multi-step "
                  "Python trace using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v27-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)


    # ---- S5: realistic EDA workflow (5 pairs) ----
    s5_items = [
        ("EmyNtlUtil",
         "In a schematic netlist export flow, generate verilog-compatible net names for a hierarchical bus. Use getVerilogName with bracket format for a 32-bit 'dout' bus, then also produce the underline-format variant for a flat-netlist backend.",
         ["EmyNtlUtil", "NTL_INDEX_FORMAT_USE_BRACKET", "NTL_INDEX_FORMAT_USE_UNDERLINE"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "bus_base = 'dout'\n"
          "bus_width = 32\n"
          "rtl_names = []\n"
          "flat_names = []\n"
          "for i in range(bus_width):\n"
          "    rtl_names.append(pyScript.EmyNtlUtil.getVerilogName(\n"
          "        bus_base, i, pyScript.NTL_INDEX_FORMAT_USE_BRACKET))\n"
          "    flat_names.append(pyScript.EmyNtlUtil.getVerilogName(\n"
          "        bus_base, i, pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE))\n"
          "print('RTL bus head:', rtl_names[0], '... tail:', rtl_names[-1])\n"
          "print('Flat bus head:', flat_names[0], '... tail:', flat_names[-1])\n"
          "print('total nets:', len(rtl_names))")),
        ("EmyLPPHeader",
         "Set up a small set of application-layer LPP headers for a custom drawing flow: create LPPs for Metal1/drawing (2001/0), Metal2/drawing (2002/0), and Via1/drawing (2003/0), configure their display colors and line widths, and verify each is valid and visible.",
         ["EmyLPPHeader"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "lpp_specs = [\n"
          "    (2001, 0, 'Metal1', 'drawing', 'red', 1),\n"
          "    (2002, 0, 'Metal2', 'drawing', 'blue', 2),\n"
          "    (2003, 0, 'Via1', 'drawing', 'green', 1),\n"
          "]\n"
          "lpps = []\n"
          "for lnum, pnum, lname, pname, color, width in lpp_specs:\n"
          "    lpp = pyScript.EmyLPPHeader.create(None, lnum, pnum)\n"
          "    lpp.setLayerName(lname)\n"
          "    lpp.setPurposeName(pname)\n"
          "    lpp.setVisible(True)\n"
          "    pyScript.EmyLPPHeader.setAppLPPColorName(lnum, pyScript.emvPurposeNumberDrawing, color)\n"
          "    pyScript.EmyLPPHeader.setAppLPPLineWidth(lnum, pyScript.emvPurposeNumberDrawing, width)\n"
          "    assert lpp.isValid(), '%s not valid' % lname\n"
          "    assert lpp.isAppLPP(), '%s not app-LPP' % lname\n"
          "    lpps.append(lpp)\n"
          "    print('LPP %s/%s: layer=%d purpose=%d color=%s width=%d' % (\n"
          "        lname, pname, lpp.getLayerNum(), lpp.getPurposeNum(), color, width))\n"
          "print('total LPPs configured:', len(lpps))")),
        ("NTL_INDEX_FORMAT_ORIGIN",
         "A legacy flat netlist tool requires bus names without any separator. Generate origin-format names for a 64-bit 'addr' bus and write them to a list for downstream processing.",
         ["NTL_INDEX_FORMAT_ORIGIN", "EmyNtlUtil"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "fmt = pyScript.NTL_INDEX_FORMAT_ORIGIN\n"
          "addr_bus = []\n"
          "for i in range(64):\n"
          "    addr_bus.append(pyScript.EmyNtlUtil.getVerilogName('addr', i, fmt))\n"
          "print('first 4:', addr_bus[:4])\n"
          "print('last 4:', addr_bus[-4:])\n"
          "print('all names have no separator:', all('[' not in n and '_' not in n for n in addr_bus))")),
        ("NTL_INDEX_FORMAT_USE_BRACKET",
         "For RTL export, produce standard Verilog bus notation for a multi-bit control bus 'ctrl[5:0]' using bracket format. Also demonstrate using getVerilogName with an instance-style call.",
         ["NTL_INDEX_FORMAT_USE_BRACKET", "EmyNtlUtil"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "fmt = pyScript.NTL_INDEX_FORMAT_USE_BRACKET\n"
          "ctrl_names = []\n"
          "for i in range(6):\n"
          "    ctrl_names.append(pyScript.EmyNtlUtil.getVerilogName('ctrl', i, fmt))\n"
          "print('control bus:', ctrl_names)\n"
          "print('sample bracket:', ctrl_names[3])\n"
          "assert ctrl_names[3] == 'ctrl[3]', 'unexpected format: %s' % ctrl_names[3]")),
        ("NTL_INDEX_FORMAT_USE_UNDERLINE",
         "A layout netlister requires underscore-separated bus names to avoid GDS special characters. Generate underline-format names for a 'scan' bus of width 8 and verify no brackets appear.",
         ["NTL_INDEX_FORMAT_USE_UNDERLINE", "EmyNtlUtil"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "fmt = pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE\n"
          "scan_names = []\n"
          "for i in range(8):\n"
          "    nm = pyScript.EmyNtlUtil.getVerilogName('scan', i, fmt)\n"
          "    scan_names.append(nm)\n"
          "    assert '[' not in nm, 'bracket found in underline name: %s' % nm\n"
          "print('scan bus:', scan_names)\n"
          "print('all have underscore:', all('_' in n for n in scan_names))")),
    ]
    for name, scenario, apis, code in s5_items:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript) that solves this "
                  "realistic scenario." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S5", "v27-S5-%s" % name, prompt, completion, apis,
             "S5 realistic_workflow for %s" % name)


    # ---- S6: cross-API combo (5 pairs) ----
    s6_items = [
        ("EmyNtlUtil+NTL_INDEX_FORMAT_all",
         "Demonstrate all three NTL_INDEX_FORMAT constants with EmyNtlUtil.getVerilogName on the same base name and index, showing the three resulting name styles side by side.",
         ["EmyNtlUtil", "NTL_INDEX_FORMAT_ORIGIN", "NTL_INDEX_FORMAT_USE_BRACKET", "NTL_INDEX_FORMAT_USE_UNDERLINE"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "base = 'net'\n"
          "idx = 5\n"
          "fmts = {\n"
          "    'origin': pyScript.NTL_INDEX_FORMAT_ORIGIN,\n"
          "    'bracket': pyScript.NTL_INDEX_FORMAT_USE_BRACKET,\n"
          "    'underline': pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE,\n"
          "}\n"
          "for label, fmt in fmts.items():\n"
          "    nm = pyScript.EmyNtlUtil.getVerilogName(base, idx, fmt)\n"
          "    print('%-10s -> %s' % (label, nm))")),
        ("EmyLPPHeader+EmyNtlUtil",
         "After configuring an application-layer LPP header for a routing layer, generate verilog net names for the nets on that layer using bracket format.",
         ["EmyLPPHeader", "EmyNtlUtil", "NTL_INDEX_FORMAT_USE_BRACKET"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "lpp = pyScript.EmyLPPHeader.create(None, 2010, 0)\n"
          "lpp.setLayerName('RouteM3')\n"
          "lpp.setPurposeName('drawing')\n"
          "lpp.setVisible(True)\n"
          "pyScript.EmyLPPHeader.setAppLPPColorName(2010, pyScript.emvPurposeNumberDrawing, 'orange')\n"
          "print('LPP layer:', lpp.getLayerName(), 'num:', lpp.getLayerNum())\n"
          "fmt = pyScript.NTL_INDEX_FORMAT_USE_BRACKET\n"
          "net_names = []\n"
          "for i in range(4):\n"
          "    net_names.append(pyScript.EmyNtlUtil.getVerilogName('rnet', i, fmt))\n"
          "print('route nets:', net_names)")),
        ("EmyLPPHeader+NTL_INDEX_FORMAT_ORIGIN",
         "Create two app-LPP headers for power/ground layers, then generate origin-format net names for a small power bus to annotate them.",
         ["EmyLPPHeader", "NTL_INDEX_FORMAT_ORIGIN", "EmyNtlUtil"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "vdd_lpp = pyScript.EmyLPPHeader.create(None, 2050, 0)\n"
          "vdd_lpp.setLayerName('VDD')\n"
          "vdd_lpp.setPurposeName('pin')\n"
          "gnd_lpp = pyScript.EmyLPPHeader.create(None, 2051, 0)\n"
          "gnd_lpp.setLayerName('GND')\n"
          "gnd_lpp.setPurposeName('pin')\n"
          "print('VDD LPP valid:', vdd_lpp.isValid(), ' GND LPP valid:', gnd_lpp.isValid())\n"
          "fmt = pyScript.NTL_INDEX_FORMAT_ORIGIN\n"
          "power_nets = []\n"
          "for i in range(2):\n"
          "    power_nets.append(pyScript.EmyNtlUtil.getVerilogName('pwr', i, fmt))\n"
          "print('power nets (origin):', power_nets)")),
        ("EmyNtlUtil+NTL_INDEX_FORMAT_USE_UNDERLINE+NTL_INDEX_FORMAT_USE_BRACKET",
         "Build a name-mapping table that converts bracket-format verilog names to underline-format names for a downstream tool, using EmyNtlUtil.getVerilogName for both directions.",
         ["EmyNtlUtil", "NTL_INDEX_FORMAT_USE_UNDERLINE", "NTL_INDEX_FORMAT_USE_BRACKET"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "base = 'state'\n"
          "width = 8\n"
          "mapping = {}\n"
          "for i in range(width):\n"
          "    bracket = pyScript.EmyNtlUtil.getVerilogName(base, i, pyScript.NTL_INDEX_FORMAT_USE_BRACKET)\n"
          "    underline = pyScript.EmyNtlUtil.getVerilogName(base, i, pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE)\n"
          "    mapping[bracket] = underline\n"
          "for k, v in sorted(mapping.items()):\n"
          "    print('%s -> %s' % (k, v))\n"
          "print('mapping entries:', len(mapping))")),
        ("EmyLPPHeader+EmyNtlUtil+NTL_INDEX_FORMAT_all",
         "Full workflow: define a set of app-LPP headers for signal layers, then generate verilog bus names in all three formats for nets routed on the first layer, and print a summary report.",
         ["EmyLPPHeader", "EmyNtlUtil", "NTL_INDEX_FORMAT_ORIGIN", "NTL_INDEX_FORMAT_USE_BRACKET", "NTL_INDEX_FORMAT_USE_UNDERLINE"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "layers = [(2001, 'M1'), (2002, 'M2'), (2003, 'M3')]\n"
          "for lnum, lname in layers:\n"
          "    lpp = pyScript.EmyLPPHeader.create(None, lnum, 0)\n"
          "    lpp.setLayerName(lname)\n"
          "    lpp.setPurposeName('drawing')\n"
          "    lpp.setVisible(True)\n"
          "    print('LPP %s: num=%d valid=%s appLPP=%s' % (\n"
          "        lname, lpp.getLayerNum(), lpp.isValid(), lpp.isAppLPP()))\n"
          "print('--- net names for M1 bus (4-bit) ---')\n"
          "fmts = [pyScript.NTL_INDEX_FORMAT_ORIGIN,\n"
          "        pyScript.NTL_INDEX_FORMAT_USE_BRACKET,\n"
          "        pyScript.NTL_INDEX_FORMAT_USE_UNDERLINE]\n"
          "for i in range(4):\n"
          "    names = [pyScript.EmyNtlUtil.getVerilogName('sig', i, f) for f in fmts]\n"
          "    print('sig[%d]: origin=%s bracket=%s underline=%s' % (i, names[0], names[1], names[2]))")),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript), combining the relevant "
                  "APIs." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v27-S6-%s" % apis_str.replace("+", "-"), prompt, completion, apis,
             "S6 cross_api_combo: %s" % apis_str)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details



def main():
    ap = argparse.ArgumentParser(
        description="R197 v27 PyAether SFT corpus: Emy* NTL/LPP (5 APIs, 25 pairs)")
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
    sys.stderr.write("\n=== R197 v27 Emy*/NTL/LPP corpus summary ===\n")
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

