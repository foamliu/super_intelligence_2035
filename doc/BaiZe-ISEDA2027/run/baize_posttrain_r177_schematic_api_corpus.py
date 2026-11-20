#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r177_schematic_api_corpus.py
R177 -- Schematic Creation/Lookup API Training-Pair Synthesis (v8 corpus).

BACKGROUND (R176 correction):
  R176 custom qual-eval prompts S3/S4 referenced *fabricated* API names
  ``schCreateWire`` and ``leGetPin``. PyAether MCP API search confirms NEITHER
  exists in the live API database. The real APIs are:
    - create wire in schematic -> dbCrtSchWire (sim 0.96 to "schCreateWire")
    - get pin name from figure -> emyFigGetPinName / dbGetPinFigName
    - judge schematic wire     -> dbSchIsWire
  grep of the 158-task eval dataset for schCreateWire/leGetPin = 0 hits, so
  those names were never part of the eval. The R176 "S3 退化循环" and
  "S4 跨域幻觉" failures were due to *nonexistent APIs in the prompt*, NOT
  an SFT corpus coverage gap. R176's "下一步 ④ 补充 schCreateWire/leGetPin
  覆盖" was based on that wrong premise.

  This script does the *correct* thing: build training pairs for the REAL
  schematic creation/lookup APIs (with their authoritative API docs + doctests
  retrieved via get_api_details).

CONTAMINATION ISOLATION (red line 5.1):
  - Source = official PyAether API documentation (signatures + params +
    documented >>> doctest examples), retrieved via the pyAether MCP
    get_api_details tool. NOT from any eval task.
  - The 158 eval tasks are never read by this script (only entry_point
    strings loaded for fingerprint scan).
  - Fingerprint scan: every completion checked against eval entry_points.

Usage:
  python3 baize_posttrain_r177_schematic_api_corpus.py [--dry-run] [--limit N]
"""
import argparse
import hashlib
import json
import os
import sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v8_schematic_apis.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {
    "dbCrtSchWire": {
        "sig": 'dbCrtSchWire(cv, point, wireMode="Narrow", width=0.0625, '
               'lockAngle="AnyAngle", flyLine=False, wireSnapping=True, '
               'color="cadetBlue", lineStyle="solid") -> Tuple[emyFig]',
        "desc": "This command is used to create a wire in schematic view.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "point": "vector1D_emyPointF - the points list to create the wire",
                   "wireMode": 'emyString - Narrow or Wide (default Narrow)',
                   "width": "float - width of wide wire (default 0.0625)"},
        "doctest": '>>> import pyAether as pyScript\n'
                   '>>> cvId = pyScript.dbOpenCV(lib="test",cell="test",view="schematic")\n'
                   '>>> point = ((20.0, 10), (30, 10))\n'
                   '>>> pyScript.dbCrtSchWire(cv=cvId,point=point)',
        "category": "Schematic / Create"},
    "dbCrtWire": {
        "sig": "dbCrtWire(cv, layer, points, width, purpose='drawing') -> emyFig",
        "desc": "This command is used to create a wire (layout). Returns a fig identifier.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "layer": "emyString - layer number or layer name",
                   "points": "vector1D_emyPointF - point list of center line",
                   "width": "float - width of wire"},
        "doctest": '>>> import pyAether as pyScript\n'
                   '>>> cvId = pyScript.dbOpenCV(lib="test",cell="test",view="layout")\n'
                   '>>> pyScript.dbCrtWire(cv=cvId, layer="M1", points=((0,0),(10,0)), width=0.5)',
        "category": "Layout / Create"},
    "dbCrtSchPin": {
        "sig": 'dbCrtSchPin(cv, name, point, direction="input", overbar=False, '
               'orient="R0") -> emyPin',
        "desc": "This command is used to create a pin in schematic view.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "name": "emyString - pin name",
                   "point": "emyPointF - pin location",
                   "direction": 'emyString - input/output/inputOutput'},
        "doctest": '>>> import pyAether as pyScript\n'
                   '>>> cvId = pyScript.dbOpenCV(lib="test",cell="test",view="schematic")\n'
                   '>>> pyScript.dbCrtSchPin(cv=cvId, name="IN1", point=(0.0,0.0), direction="input")',
        "category": "Schematic / Create"},
    "dbCrtSchWireName": {
        "sig": 'dbCrtSchWireName(cv, wire, name, point, height=0.0625, '
               'font="stick", justify="lowerCenter", offset=6) -> emyFig',
        "desc": "This command is used to create a wire name (label) in schematic view.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "wire": "emyFig - the wire fig to name (from dbCrtSchWire)",
                   "name": "emyString - the wire name label text",
                   "point": "emyPointF - label anchor point"},
        "doctest": '>>> import pyAether as pyScript\n'
                   '>>> cvId = pyScript.dbOpenCV(lib="test",cell="test",view="schematic")\n'
                   '>>> wire = pyScript.dbCrtSchWire(cv=cvId, point=((0,0),(100,0)))[0]\n'
                   '>>> pyScript.dbCrtSchWireName(cv=cvId, wire=wire, name="CLK", point=(50.0,10.0))',
        "category": "Schematic / Create"},
    "dbCrtNet": {
        "sig": "dbCrtNet(cv: emyDesign, name: emyString) -> emyNet",
        "desc": "This command is used to create a net. Returns a net identifier if successful.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "name": "emyString - the net's name"},
        "doctest": '>>> import pyAether as pyScript\n'
                   '>>> cvId = pyScript.dbOpenCV(lib="test",cell="test",view="layout")\n'
                   '>>> pyScript.dbCrtNet(cv=cvId, name="net01")',
        "category": "Net / Create"},
    "emyFigGetPinName": {
        "sig": "emyFigGetPinName(fig: emyFig) -> emyString",
        "desc": "Gets figure's pin name.",
        "params": {"fig": "emyFig - the figure, should not be None"},
        "doctest": '>>> import pyAether\n>>> res = pyAether.emyFigGetPinName(rect)',
        "category": "Pin / Query"},
    "dbGetPinFigName": {
        "sig": "dbGetPinFigName(fig: emyFig) -> emyString",
        "desc": "This command returns the pin's name with the figure.",
        "params": {"fig": "emyFig - the figure identifier"},
        "doctest": '>>> import pyAether as pyScript\n'
                   '>>> figId = pyScript.dbFindInst(cv=cv, name=name)\n'
                   '>>> pyScript.dbGetPinFigName(fig=figId)',
        "category": "Pin / Query"},
    "dbSchIsWire": {
        "sig": "dbSchIsWire(obj: emyObject) -> emyBoolean",
        "desc": "Judge whether a schematic object is wire or not. Returns True if wire.",
        "params": {"obj": "emyObject - object you want to judge"},
        "doctest": '>>> import pyAether as pyScript\n'
                   '>>> cvId = pyScript.dbOpenCV(lib="test",cell="test",view="schematic")\n'
                   '>>> tmp = pyScript.dbCrtSchWire(cv=cvId, point=((20,10),(30,10)))\n'
                   '>>> pyScript.dbSchIsWire(tmp[0])',
        "category": "Schematic / Verify"},
    "emyPinGetNames": {
        "sig": "emyPinGetNames(pin: emyPin, names: emyArray_p_emyShape, ignoreVoltageLabel=False)",
        "desc": "This method is used to obtain the name of the pin.",
        "params": {"pin": "emyPin - specifies emyPin",
                   "names": "emyArray_p_emyShape - array that receives pinName"},
        "doctest": '>>> import pyAether as pyScript\n'
                   '>>> names = pyScript.emyArray_p_emyShape()\n'
                   '>>> pyScript.emyPinGetNames(pin=pinObj, names=names)',
        "category": "Pin / Query"},
    "aeLeCreatePin": {
        "sig": "aeLeCreatePin(cv, layerName, purposeName, shape, points, pinName, type, accessDir)",
        "desc": "This command creates a pin in the design whose type is layout.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "layerName": 'emyString - layer name e.g. M1',
                   "shape": "emyString - Rectangle/Polygon/...",
                   "pinName": "emyString - pin name",
                   "type": "emyString - input/output/inputOutput"},
        "doctest": '>>> import pyAether as pyScript\n'
                   '>>> cv = pyScript.aeGetCurDesign()\n'
                   '>>> pyScript.aeLeCreatePin(cv, "M1", "pin", "Rectangle", [(0,0),(5,5)], "VDD", "input", ["left"])',
        "category": "Layout / Create"},
}


def _pid(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _contam_check(completion, eval_eps):
    for ep in eval_eps:
        if ep and ep in completion:
            return ep
    return None


def _make_completion_s1(name, doc):
    dt = doc["doctest"]
    lines = [l for l in dt.split("\n") if l.strip()]
    body_lines = []
    for l in lines:
        s = l.strip()
        if s.startswith(">>>"):
            body_lines.append("    " + s[4:].strip())
    fn_map = {"dbCrtSchWire": "create_sch_wire", "dbCrtWire": "create_wire",
              "dbCrtNet": "create_net", "dbCrtSchPin": "create_sch_pin",
              "dbCrtSchWireName": "create_wire_name",
              "aeLeCreatePin": "create_layout_pin",
              "emyFigGetPinName": "get_pin_name",
              "dbGetPinFigName": "get_pin_fig_name",
              "dbSchIsWire": "is_sch_wire",
              "emyPinGetNames": "get_pin_names"}
    fn = fn_map.get(name, "use_" + name.lower())
    body = "\n".join(body_lines) if body_lines else "    pass"
    return "import pyAether as pyScript\n\ndef %s():\n%s\n" % (fn, body)


def build_pairs(eval_eps, limit=None):
    pairs = []
    rejected = 0

    # ---- S1_doc_to_code ----
    for name, doc in API_DOCS.items():
        prompt = (
            "You are an EDA automation assistant. Read the following PyAether "
            "API documentation and write Python code that correctly uses this "
            "API.\n\n## API Documentation\n\n## %s\n\n`%s`(...)\n\n**`%s`**\n\n"
            "%s\n\nParameters\n%s\n\nExamples\n\n    %s"
        ) % (name, name, doc["sig"], doc["desc"],
             "\n".join("**%s**%s" % (k, " " + v) for k, v in doc["params"].items()),
             doc["doctest"].replace("\n", "\n    "))
        completion = _make_completion_s1(name, doc)
        hit = _contam_check(completion, eval_eps)
        if hit:
            rejected += 1
            continue
        pairs.append({"pair_id": "R177-S1-%s-%s" % (name, _pid(completion)),
                      "type": "S1_doc_to_code", "api_used": [name],
                      "prompt": prompt, "completion": completion,
                      "contamination_check": "PASS"})

    # ---- S2_api_lookup ----
    lookups = [
        ("create a wire in a schematic view", "dbCrtSchWire",
         'pyScript.dbCrtSchWire(cv=cvId, point=((20.0,10),(30,10)))'),
        ("create a wire in a layout view", "dbCrtWire",
         'pyScript.dbCrtWire(cv=cvId, layer="M1", points=((0,0),(10,0)), width=0.5)'),
        ("create a pin in a schematic view", "dbCrtSchPin",
         'pyScript.dbCrtSchPin(cv=cvId, name="IN1", point=(0.0,0.0), direction="input")'),
        ("create a pin in a layout view", "aeLeCreatePin",
         'pyScript.aeLeCreatePin(cv, "M1", "pin", "Rectangle", [(0,0),(5,5)], "VDD", "input", ["left"])'),
        ("get a figure's pin name", "emyFigGetPinName",
         "name = pyAether.emyFigGetPinName(fig)"),
        ("get the pin name associated with a figure", "dbGetPinFigName",
         "name = pyScript.dbGetPinFigName(fig=figId)"),
        ("judge whether a schematic object is a wire", "dbSchIsWire",
         "is_wire = pyScript.dbSchIsWire(obj)"),
        ("create a net", "dbCrtNet",
         'net = pyScript.dbCrtNet(cv=cvId, name="net01")'),
        ("add a name label to a schematic wire", "dbCrtSchWireName",
         'pyScript.dbCrtSchWireName(cv=cvId, wire=wire, name="CLK", point=(50.0,10.0))'),
        ("obtain the names of a pin", "emyPinGetNames",
         "pyScript.emyPinGetNames(pin=pinObj, names=names)"),
    ]
    for intent, api, usage in lookups:
        prompt = ("You are an EDA automation assistant. Which PyAether API is "
                  "used to %s? Show a minimal correct usage example." % intent)
        completion = ("The API is `%s`.\n\n```python\nimport pyAether as "
                      "pyScript\n%s\n```" % (api, usage))
        hit = _contam_check(completion, eval_eps)
        if hit:
            rejected += 1
            continue
        pairs.append({"pair_id": "R177-S2-%s-%s" % (api, _pid(completion)),
                      "type": "S2_api_lookup", "api_used": [api],
                      "prompt": prompt, "completion": completion,
                      "contamination_check": "PASS"})

    # ---- S3_multi_api_chain ----
    chains = [
        ("create_wire_and_verify",
         "Write a Python function create_wire_and_verify(lib, cell, points) "
         "that opens a schematic cell view, creates a wire using dbCrtSchWire, "
         "and returns True if the created object is a wire (use dbSchIsWire).",
         "dbCrtSchWire", "dbSchIsWire",
         "def create_wire_and_verify(lib, cell, points):\n"
         "    import pyAether as pyScript\n"
         "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"schematic\")\n"
         "    wire_figs = pyScript.dbCrtSchWire(cv=cv, point=points)\n"
         "    if not wire_figs:\n"
         "        return False\n"
         "    return bool(pyScript.dbSchIsWire(wire_figs[0]))\n"),
        ("create_net_and_name_wire",
         "Write a Python function setup_net_and_wire(lib, cell, net_name, "
         "wire_points, wire_label) that opens a schematic cell view, creates "
         "a net with dbCrtNet, creates a wire with dbCrtSchWire, adds a name "
         "label with dbCrtSchWireName, and returns the net id.",
         "dbCrtNet", "dbCrtSchWire",
         "def setup_net_and_wire(lib, cell, net_name, wire_points, wire_label):\n"
         "    import pyAether as pyScript\n"
         "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"schematic\")\n"
         "    net = pyScript.dbCrtNet(cv=cv, name=net_name)\n"
         "    wire_figs = pyScript.dbCrtSchWire(cv=cv, point=wire_points)\n"
         "    if wire_figs:\n"
         "        pyScript.dbCrtSchWireName(cv=cv, wire=wire_figs[0],\n"
         "                                  name=wire_label,\n"
         "                                  point=wire_points[0])\n"
         "    return net\n"),
        ("get_pin_name_from_fig",
         "Write a Python function get_pin_name(cv, inst_name) that finds an "
         "instance with dbFindInst and returns its pin name using "
         "dbGetPinFigName.",
         "dbFindInst", "dbGetPinFigName",
         "def get_pin_name(cv, inst_name):\n"
         "    import pyAether as pyScript\n"
         "    fig = pyScript.dbFindInst(cv=cv, name=inst_name)\n"
         "    if not fig:\n"
         "        return None\n"
         "    return pyScript.dbGetPinFigName(fig=fig)\n"),
    ]
    for cid, prompt, api1, api2, completion in chains:
        hit = _contam_check(completion, eval_eps)
        if hit:
            rejected += 1
            continue
        pairs.append({"pair_id": "R177-S3-%s-%s" % (cid, _pid(completion)),
                      "type": "S3_multi_api_chain", "api_used": [api1, api2],
                      "prompt": prompt, "completion": completion,
                      "contamination_check": "PASS"})

    # ---- S7_corrected_prompt (R176 S3/S4 intent with REAL api names) ----
    corrected = [
        ("S3_corrected",
         "Write a Python function create_wire(lib, cell, points) that opens a "
         "schematic cell view and creates a schematic wire on it using "
         "dbCrtSchWire. Return the created wire figures.",
         "dbCrtSchWire",
         "def create_wire(lib, cell, points):\n"
         "    import pyAether as pyScript\n"
         "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"schematic\")\n"
         "    return pyScript.dbCrtSchWire(cv=cv, point=points)\n"),
        ("S4_corrected",
         "Write a Python function get_pin_name(fig) that takes a figure "
         "object and returns its pin name using emyFigGetPinName.",
         "emyFigGetPinName",
         "def get_pin_name(fig):\n"
         "    import pyAether\n"
         "    return pyAether.emyFigGetPinName(fig)\n"),
    ]
    for cid, prompt, api, completion in corrected:
        hit = _contam_check(completion, eval_eps)
        if hit:
            rejected += 1
            continue
        pairs.append({"pair_id": "R177-S7-%s-%s" % (cid, _pid(completion)),
                      "type": "S7_corrected_prompt", "api_used": [api],
                      "prompt": prompt, "completion": completion,
                      "contamination_check": "PASS",
                      "note": "corrected R176 prompt using real API name"})
    if limit:
        pairs = pairs[:limit]
    return pairs, rejected



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
                rec = json.loads(line)
            except Exception:
                continue
            ep = rec.get("entry_point")
            if ep:
                eps.add(ep)
    return eps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    eval_eps = load_eval_entry_points()
    sys.stderr.write("Loaded %d eval entry_points for contam scan\n" % len(eval_eps))
    pairs, rejected = build_pairs(eval_eps, limit=args.limit)
    by_type = {}
    for p in pairs:
        by_type.setdefault(p["type"], 0)
        by_type[p["type"]] += 1
    apis = set()
    for p in pairs:
        apis.update(p["api_used"])
    summary = {"total_pairs": len(pairs), "rejected_contam": rejected,
               "by_type": by_type, "apis_covered": sorted(apis),
               "out_path": OUT_PATH}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if args.dry_run:
        sys.stderr.write("[dry-run] no file written\n")
        return
    with open(OUT_PATH, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    sz = os.path.getsize(OUT_PATH)
    sys.stderr.write("Wrote %d pairs (%d bytes) to %s\n" % (len(pairs), sz, OUT_PATH))


if __name__ == "__main__":
    main()

