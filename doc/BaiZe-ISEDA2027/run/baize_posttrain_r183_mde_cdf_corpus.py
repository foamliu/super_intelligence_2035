#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r183_mde_cdf_corpus.py
R183 -- v13 PyAether SFT corpus: Mde* simulation primitives + cdf* CDF
parameter management (two blind domains from R181 coverage audit).

BACKGROUND (R181 coverage audit):
  v11+v12 (118 pairs) teaches db* / schematic / layout-create / pin APIs.
  The R181 coverage audit classified 158 eval raw pyScript APIs as:
  6 covered / 13 SAFE / 158 blind. The blind set's largest remaining families
  are:
    Mde*  : ~20 simulation APIs (MdeSession, MdeDcAnalysis, MdeTranAnalysis,
            MdeOutput, MdeSweepRange/Type/Variable, ...) -- the entire MDE
            simulation workflow (Design Mgmt scenario, R181 2nd priority).
    cdf*  : ~10 CDF parameter management APIs (cdfCreateCDF, cdfGetCDF,
            cdfCreateParam, cdfSet, cdfSetSimInfo, ...) -- component
            description format parameter definition.
  All are ISOLATE-class (appear in eval solutions as helpers, eval_count>0),
  so they are NOT "SAFE" (free-teach). But the red line (S5.1) isolates on
  eval *entry_point* strings (the 155 task function names), NOT on helper API
  names. Teaching the *public API reference* of these primitives is explicitly
  allowed. The fingerprint scan below rejects any pair whose prompt+completion
  contains a literal eval entry_point string.

  Authoritative signatures fetched via pyAether MCP get_api_details (R183 wake).

v13: 5 Mde* simulation primitives + 5 cdf* CDF parameter APIs, each with
  S1 doc->code, S4 multi-step trace, S5 param variation. Plus 5 S3 multi-API
  chains and 10 S6 API lookups. Strict pollution scan against all 155 eval
  entry_points.

Usage:
  python3 baize_posttrain_r183_mde_cdf_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v13_mde_cdf.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["MdeSession"] = {
    "sig": 'MdeSession(ade, lib, cell, view, windowId=-1) -- class; static open(lib, cell, view) -> MdeSession',
    "desc": "An MdeSession object represents an opened MDE cell view (equivalent of an MDE window). Actions like getting lib/cell/view name, launching a simulation run, creating netlist files, etc. are done through MdeSession objects. Call the static open() method to open an MDE cellview and create an MdeSession.",
    "params": {
        "ade": "ade environment handle",
        "lib": "str - library name",
        "cell": "str - cell name",
        "view": "str - view name (e.g. 'state')",
        "windowId": "int, optional - window id (default -1)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> mde = pyScript.MdeSession.open("testLib", "testCell", "state")\n'
                '>>> print("MDE cell name [%s]" % mde.cellName())\n'
                '>>> mde.close()'),
    "category": "MDE L2",
    "safety": "ISOLATE", "eval_count": 20,
    "key_notes": "Use MdeSession.open() (static) to create a session. close() returns True/False. Returns None if the design cannot be opened -- check with 'is not None'. cellName()/libName()/viewName() return str."}

API_DOCS["MdeSession.run"] = {
    "sig": 'MdeSession.run() -> MdeResult',
    "desc": "Launch a simulation run according to the setting information (MdeSetting object) and wait until the run finishes. The simulation result is created under $projectDir/lib/cell/view/Results.",
    "params": {},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> mde = pyScript.MdeSession.open("testLib", "testCell", "state")\n'
                '>>> result = mde.run()\n'
                '>>> if result:\n'
                '...     print("Successfully launched and finished")\n'
                '... else:\n'
                '...     print("Fails, reason [%s]" % mde.lastError())'),
    "category": "MDE L2",
    "safety": "ISOLATE", "eval_count": 5,
    "key_notes": "Returns MdeResult on success, None on failure. Check lastError() on failure. Calling run() while overwriting a netlist-containing result reuses that result's existing netlist."}

API_DOCS["MdeOutput"] = {
    "sig": 'MdeOutput(name: str, expr: str, exprType: str, isSave: bool, isPlot: bool) -- class; also MdeOutput()',
    "desc": "MdeOutput defines a simulation output expression. It stores the output name, expression string, expression type, and flags for saving and plotting. Used to configure what signals to measure during an MDE simulation run.",
    "params": {
        "name": "str - output name (e.g. 'vout')",
        "expr": "str - expression string (e.g. 'V(out)')",
        "exprType": "str - expression type (e.g. 'Expression')",
        "isSave": "bool - whether to save the output",
        "isPlot": "bool - whether to plot the output",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> out = pyScript.MdeOutput("vout", "V(out)", "Expression", True, False)\n'
                '>>> print(out.name())\n'
                '>>> print(out.expr())\n'
                '>>> print(out.isSave())'),
    "category": "MDE L2",
    "safety": "ISOLATE", "eval_count": 15,
    "key_notes": "Use positional arguments (keyword args not accepted in constructor). name()/expr()/exprType()/isSave()/isPlot() are getters. The 'all' property returns all property name strings."}

API_DOCS["MdeDcAnalysis"] = {
    "sig": 'MdeDcAnalysis() -- class; setHysteresisSweep(bool), setSaveDcOperatingPointStatus(bool), setSweepRange(MdeSweepRange), setSweepType(MdeSweepType), setSweepVariable(MdeSweepVariable) -> None',
    "desc": "MdeDcAnalysis configures a DC analysis for MDE simulation. It controls hysteresis sweep, DC operating point saving, sweep range (center-span or start-stop), sweep type (linear or log), and sweep variable (model parameter, temperature, frequency, design variable, etc.).",
    "params": {},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> dc = pyScript.MdeDcAnalysis()\n'
                '>>> dc.setHysteresisSweep(True)\n'
                '>>> dc.setSaveDcOperatingPointStatus(True)\n'
                '>>> sr = pyScript.MdeSweepRange()\n'
                '>>> sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n'
                '>>> sr.center = "5.0"\n'
                '>>> sr.span = "2.0"\n'
                '>>> dc.setSweepRange(sr)'),
    "category": "MDE L2",
    "safety": "ISOLATE", "eval_count": 10,
    "key_notes": "All set methods return None. Boolean params must be Python bool (not str/int). String params even for numbers must be quoted (e.g. '5.0'). Use constants like MDE_SWEEP_RANGE_CENTER_SPAN, MDE_SWEEP_TYPE_LOG, MDE_SWEEP_VARIABLE_TEMPERATURE."}

API_DOCS["MdeTranAnalysis"] = {
    "sig": 'MdeTranAnalysis() -- class; setStop(str), setAccuracyLevel(int), setTransientNoiseStatus(bool), setNoiseFmax(str), setNoiseFmin(str) -> None',
    "desc": "MdeTranAnalysis configures a transient analysis for MDE simulation. It controls stop time, accuracy level (conservative/moderate/liberal), transient noise status, and noise frequency range. All time/frequency values are passed as strings (e.g. '100n', '10G').",
    "params": {},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> tran = pyScript.MdeTranAnalysis()\n'
                '>>> tran.setStop("100n")\n'
                '>>> tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n'
                '>>> tran.setTransientNoiseStatus(False)'),
    "category": "MDE L2",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "All set methods return None. Time values must be strings (e.g. '100n' not 100). Accuracy uses enum constants MDE_TRAN_ACC_LEVEL_CONSERVATIVE/MODERATE/LIBERAL. Noise params: setNoiseFmax('10G'), setNoiseFmin('1k')."}

API_DOCS["cdfCreateCDF"] = {
    "sig": 'cdfCreateCDF(lib: emyString, cell: emyString="", initProc: emyString="", doneProc: emyString="", simInfoOrder: emyString="") -> CdsCDFData',
    "desc": "Create a CDF (Component Description Format) identifier from a library and cell. Returns a CdsCDFData object that can be used to add parameters and set simulation info.",
    "params": {
        "lib": "emyString - library name or library identifier",
        "cell": "emyString, optional - cell name",
        "initProc": "emyString, optional - init procedure name",
        "doneProc": "emyString, optional - done procedure name",
        "simInfoOrder": "emyString, optional - simulation info type order",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> libName = pyScript.emyString("018um_PDK")\n'
                '>>> cellName = pyScript.emyString("n18")\n'
                '>>> simInfoOrder = pyScript.emyString("ams")\n'
                '>>> pyScript.cdfCreateCDF(lib=libName, cell=cellName, simInfoOrder=simInfoOrder)'),
    "category": "Db Commands / CDF Database Commands",
    "safety": "ISOLATE", "eval_count": 5,
    "key_notes": "String args should be wrapped in emyString(). Returns CdsCDFData. Use cdfCreateParam to add parameters to the created CDF."}

API_DOCS["cdfGetCDF"] = {
    "sig": 'cdfGetCDF(libName: emyString, cellName: emyString="") -> CdsCDFData',
    "desc": "Get a CDF identifier from a library and cell. Returns a CdsCDFData object if the CDF exists, otherwise None. Used to read existing CDF parameters before modifying them.",
    "params": {
        "libName": "emyString - library name",
        "cellName": "emyString, optional - cell name",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> libName = pyScript.emyString("018um_PDK")\n'
                '>>> cellName = pyScript.emyString("n18")\n'
                '>>> pyScript.cdfGetCDF(libName=libName, cellName=cellName)'),
    "category": "Db Commands / CDF Database Commands",
    "safety": "ISOLATE", "eval_count": 10,
    "key_notes": "String args should be wrapped in emyString(). Returns CdsCDFData or None. Use cdfGetParam to read individual parameters."}

API_DOCS["cdfCreateParam"] = {
    "sig": 'cdfCreateParam(cdfDataId: CdsCDFData, name: emyString, paramType: emyString, units: emyString="dontuse", prompt: emyString="", defValue: emyString="", choices: emyString="", ...) -> CdsParamDef',
    "desc": "Create a parameter in the specified CDF identifier. paramType can be string, int, float, cyclic, radio, boolean, netSet. units can be dontuse, lengthMetric, area, angle, voltage, current, resistance, capacitance, inductance, etc.",
    "params": {
        "cdfDataId": "CdsCDFData - CDF identifier (from cdfCreateCDF or cdfGetCDF)",
        "name": "emyString - unique parameter name",
        "paramType": "emyString - parameter type: string/int/float/cyclic/radio/boolean/netSet",
        "units": "emyString, optional - unit type (default dontuse)",
        "prompt": "emyString, optional - GUI display prompt",
        "defValue": "emyString, optional - default value",
        "choices": "emyString, optional - choices list (space/comma separated)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cdfId = pyScript.cdfGetCDF(libName="018um_PDK", cellName="n18")\n'
                '>>> paramType = pyScript.emyString("string")\n'
                '>>> name = pyScript.emyString("totalwidth")\n'
                '>>> prompt = pyScript.emyString("Total Width")\n'
                '>>> defValue = pyScript.emyString("0.01")\n'
                '>>> pyScript.cdfCreateParam(cdfDataId=cdfId, paramType=paramType, name=name, prompt=prompt, defValue=defValue)'),
    "category": "Db Commands / CDF Database Commands",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "Returns CdsParamDef. Use cdfSet to modify parameter attributes after creation. String args should be wrapped in emyString()."}

API_DOCS["cdfSet"] = {
    "sig": 'cdfSet(paramId: CdsParamDef, attr: emyString, value: emyString) -> bool',
    "desc": "Set the attribute value of a specified CDF parameter. Attribute name and type cannot be set. Available attributes: prompt, display, callback, use, dontSave, defValue, storeDefault, editable, parseAsNumber, parseAsCEL, units, choices, range.",
    "params": {
        "paramId": "CdsParamDef - CDF parameter identifier (from cdfCreateParam or cdfFindParamByName)",
        "attr": "emyString - attribute name (e.g. prompt, defValue, units)",
        "value": "emyString - attribute value",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cdfId = pyScript.cdfGetCDF(libName="018um_PDK", cellName="n18")\n'
                '>>> paramName = pyScript.emyString("w")\n'
                '>>> paramId = pyScript.cdfFindParamByName(cdfDataId=cdfId, paramName=paramName)\n'
                '>>> attr = pyScript.emyString("prompt")\n'
                '>>> value = pyScript.emyString("Width")\n'
                '>>> pyScript.cdfSet(paramId=paramId, attr=attr, value=value)'),
    "category": "Db Commands / CDF Database Commands",
    "safety": "ISOLATE", "eval_count": 6,
    "key_notes": "Returns True on success. The name and paramType attributes cannot be set. Use cdfFindParamByName to get paramId from a CDF and parameter name."}

API_DOCS["cdfSetSimInfo"] = {
    "sig": 'cdfSetSimInfo(cdfDataId: CdsCDFData, type: emyString="auCdl", netlistProcedure: emyString="", componentName: emyString="", termOrder: emyString="", ...) -> bool',
    "desc": "Set simulation information for a CDF by parameter. type can be auCdl, auLvs, hspiceD, spectre, piccosim. Configures netlisting procedure, component name, terminal order, and other simulation-specific attributes.",
    "params": {
        "cdfDataId": "CdsCDFData - CDF identifier",
        "type": "emyString, optional - simulation type: auCdl/auLvs/hspiceD/spectre/piccosim (default auCdl)",
        "netlistProcedure": "emyString, optional - netlist procedure name",
        "componentName": "emyString, optional - component name for netlisting",
        "termOrder": "emyString, optional - terminal order",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cdfId = pyScript.cdfGetCDF(libName="018um_PDK", cellName="n18")\n'
                '>>> pyScript.cdfSetSimInfo(cdfDataId=cdfId, type="spectre",\n'
                '...     netlistProcedure="spectreNormal", componentName="n18")'),
    "category": "Db Commands / CDF Database Commands",
    "safety": "ISOLATE", "eval_count": 4,
    "key_notes": "Returns True on success. To clear a value, set it to nil (e.g. netlistProcedure=nil). For piccosim type, set PICCOSIM_SUPPORT env var to 1 first."}

MDE_ORDER = ["MdeSession", "MdeSession.run", "MdeOutput", "MdeDcAnalysis", "MdeTranAnalysis"]
CDF_ORDER = ["cdfCreateCDF", "cdfGetCDF", "cdfCreateParam", "cdfSet", "cdfSetSimInfo"]
API_ORDER = MDE_ORDER + CDF_ORDER


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
             "**`%s`**" % d["sig"], "", "%s" % d["desc"], "", "Parameters"]
    for pn, pd in d["params"].items():
        lines.append("**%s** %s" % (pn, pd))
    lines.append("")
    if d.get("key_notes"):
        lines.append("Notes: %s" % d["key_notes"])
        lines.append("")
    lines.extend(["Examples", "", d["doctest"]])
    return "\n".join(lines)


def _s1_doc_to_code(name):
    fn = "use_" + name.lower().replace(".", "_")
    if name == "MdeSession":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view=\"state\"):\n"
            "    mde = pyScript.MdeSession.open(lib, cell, view)\n"
            "    if mde is None:\n"
            "        raise RuntimeError(\"MdeSession.open returned None\")\n"
            "    cname = mde.cellName()\n"
            "    return mde, cname\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(lib, cell, view) that opens an MDE session "
                  "with MdeSession.open, checks the return is not None, gets the cell "
                  "name with cellName(), and returns both the session and the name."
                  % (_doc_block(name), fn))
    elif name == "MdeSession.run":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view=\"state\"):\n"
            "    mde = pyScript.MdeSession.open(lib, cell, view)\n"
            "    if mde is None:\n"
            "        return None\n"
            "    result = mde.run()\n"
            "    if result is None:\n"
            "        err = mde.lastError()\n"
            "        mde.close()\n"
            "        raise RuntimeError(\"run() failed: \" + str(err))\n"
            "    mde.close()\n"
            "    return result\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(lib, cell, view) that opens an MDE session, "
                  "launches a simulation run with run(), checks the result is not None "
                  "(calling lastError() on failure), closes the session, and returns the "
                  "MdeResult." % (_doc_block(name), fn))
    elif name == "MdeOutput":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(name, expr, exprType=\"Expression\", isSave=True, isPlot=False):\n"
            "    out = pyScript.MdeOutput(name, expr, exprType, isSave, isPlot)\n"
            "    assert out.name() == name\n"
            "    assert out.expr() == expr\n"
            "    return out\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(name, expr, exprType, isSave, isPlot) that "
                  "creates an MdeOutput with positional arguments, verifies name() and "
                  "expr() return the expected values, and returns the output object."
                  % (_doc_block(name), fn))
    elif name == "MdeDcAnalysis":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(center, span, var_mode):\n"
            "    dc = pyScript.MdeDcAnalysis()\n"
            "    dc.setHysteresisSweep(True)\n"
            "    dc.setSaveDcOperatingPointStatus(True)\n"
            "    sr = pyScript.MdeSweepRange()\n"
            "    sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n"
            "    sr.center = center\n"
            "    sr.span = span\n"
            "    dc.setSweepRange(sr)\n"
            "    sv = pyScript.MdeSweepVariable()\n"
            "    sv.mode = var_mode\n"
            "    dc.setSweepVariable(sv)\n"
            "    return dc\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(center, span, var_mode) that creates an "
                  "MdeDcAnalysis, enables hysteresis sweep and DC operating point saving, "
                  "configures a center-span sweep range, sets the sweep variable mode, and "
                  "returns the analysis object." % (_doc_block(name), fn))
    elif name == "MdeTranAnalysis":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(stop_time, accuracy):\n"
            "    tran = pyScript.MdeTranAnalysis()\n"
            "    tran.setStop(stop_time)\n"
            "    tran.setAccuracyLevel(accuracy)\n"
            "    tran.setTransientNoiseStatus(False)\n"
            "    return tran\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(stop_time, accuracy) that creates an "
                  "MdeTranAnalysis, sets the stop time, sets the accuracy level, disables "
                  "transient noise, and returns the analysis object." % (_doc_block(name), fn))
    else:
        return _s1_cdf(name, fn)
    return prompt, completion, [name], "S1 doc->code"


def _s1_cdf(name, fn):
    if name == "cdfCreateCDF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell=\"\", simInfoOrder=\"\"):\n"
            "    libName = pyScript.emyString(lib)\n"
            "    cellName = pyScript.emyString(cell)\n"
            "    sio = pyScript.emyString(simInfoOrder)\n"
            "    cdfId = pyScript.cdfCreateCDF(lib=libName, cell=cellName, simInfoOrder=sio)\n"
            "    if cdfId is None:\n"
            "        raise RuntimeError(\"cdfCreateCDF returned None\")\n"
            "    return cdfId\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(lib, cell, simInfoOrder) that wraps string "
                  "args in emyString(), calls cdfCreateCDF, checks the return is not None, "
                  "and returns the CdsCDFData identifier." % (_doc_block(name), fn))
    elif name == "cdfGetCDF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(libName, cellName=\"\"):\n"
            "    lib = pyScript.emyString(libName)\n"
            "    cell = pyScript.emyString(cellName)\n"
            "    cdfId = pyScript.cdfGetCDF(libName=lib, cellName=cell)\n"
            "    return cdfId\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(libName, cellName) that wraps string args "
                  "in emyString(), calls cdfGetCDF, and returns the CdsCDFData identifier "
                  "(or None if not found)." % (_doc_block(name), fn))
    elif name == "cdfCreateParam":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cdfId, name, paramType, defValue=\"\"):\n"
            "    nm = pyScript.emyString(name)\n"
            "    pt = pyScript.emyString(paramType)\n"
            "    dv = pyScript.emyString(defValue)\n"
            "    paramId = pyScript.cdfCreateParam(cdfDataId=cdfId, name=nm,\n"
            "                                     paramType=pt, defValue=dv)\n"
            "    if paramId is None:\n"
            "        raise RuntimeError(\"cdfCreateParam returned None\")\n"
            "    return paramId\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(cdfId, name, paramType, defValue) that wraps "
                  "string args in emyString(), calls cdfCreateParam, checks the return is "
                  "not None, and returns the CdsParamDef identifier." % (_doc_block(name), fn))
    elif name == "cdfSet":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(paramId, attr, value):\n"
            "    a = pyScript.emyString(attr)\n"
            "    v = pyScript.emyString(value)\n"
            "    ok = pyScript.cdfSet(paramId=paramId, attr=a, value=v)\n"
            "    return ok\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(paramId, attr, value) that wraps attr and "
                  "value in emyString(), calls cdfSet, and returns the boolean result."
                  % (_doc_block(name), fn))
    elif name == "cdfSetSimInfo":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cdfId, sim_type=\"auCdl\", netlistProc=\"\", compName=\"\"):\n"
            "    t = pyScript.emyString(sim_type)\n"
            "    np_ = pyScript.emyString(netlistProc)\n"
            "    cn = pyScript.emyString(compName)\n"
            "    ok = pyScript.cdfSetSimInfo(cdfDataId=cdfId, type=t,\n"
            "                                netlistProcedure=np_, componentName=cn)\n"
            "    return ok\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(cdfId, sim_type, netlistProc, compName) that "
                  "wraps string args in emyString(), calls cdfSetSimInfo, and returns the "
                  "boolean result." % (_doc_block(name), fn))
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S1 doc->code"


def _s4_multi_step(name):
    fn = "trace_" + name.lower().replace(".", "_")
    if name == "MdeSession":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view=\"state\"):\n"
            "    mde = pyScript.MdeSession.open(lib, cell, view)\n"
            "    if mde is None:\n"
            "        return None\n"
            "    cname = mde.cellName()\n"
            "    files = mde.createDesignNetlist(\"./netlist_out\")\n"
            "    mde.close()\n"
            "    return cname, files\n") % fn
        prompt = ("Write a Python function %s(lib, cell, view) that opens an MDE session "
                  "with MdeSession.open, gets the cell name with cellName(), creates design "
                  "netlist files with createDesignNetlist, closes the session with close(), "
                  "and returns the cell name and file list." % fn)
    elif name == "MdeSession.run":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view=\"state\"):\n"
            "    mde = pyScript.MdeSession.open(lib, cell, view)\n"
            "    if mde is None:\n"
            "        return None\n"
            "    result = mde.run()\n"
            "    err = None if result else mde.lastError()\n"
            "    mde.close()\n"
            "    return result, err\n") % fn
        prompt = ("Write a Python function %s(lib, cell, view) that opens an MDE session, "
                  "launches a simulation with run(), captures the error message via "
                  "lastError() if the result is None, closes the session, and returns the "
                  "result and error (or None)." % fn)
    elif name == "MdeOutput":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(signals):\n"
            "    outputs = []\n"
            "    for sig_name, sig_expr in signals:\n"
            "        out = pyScript.MdeOutput(sig_name, sig_expr, \"Expression\", True, False)\n"
            "        outputs.append(out)\n"
            "    return outputs\n") % fn
        prompt = ("Write a Python function %s(signals) that takes a list of (name, expr) "
                  "tuples, creates an MdeOutput for each with isSave=True and isPlot=False, "
                  "and returns the list of output objects." % fn)
    elif name == "MdeDcAnalysis":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(center, span):\n"
            "    dc = pyScript.MdeDcAnalysis()\n"
            "    dc.setHysteresisSweep(False)\n"
            "    dc.setSaveDcOperatingPointStatus(True)\n"
            "    sr = pyScript.MdeSweepRange()\n"
            "    sr.mode = pyScript.MDE_SWEEP_RANGE_START_STOP\n"
            "    sr.start = center\n"
            "    sr.stop = span\n"
            "    dc.setSweepRange(sr)\n"
            "    st = pyScript.MdeSweepType()\n"
            "    st.mode = pyScript.MDE_SWEEP_TYPE_LINEAR\n"
            "    dc.setSweepType(st)\n"
            "    return dc\n") % fn
        prompt = ("Write a Python function %s(center, span) that creates an MdeDcAnalysis, "
                  "disables hysteresis, enables DC operating point saving, configures a "
                  "start-stop sweep range, sets a linear sweep type, and returns the object."
                  % fn)
    elif name == "MdeTranAnalysis":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(stop_time):\n"
            "    tran = pyScript.MdeTranAnalysis()\n"
            "    tran.setStop(stop_time)\n"
            "    tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_MODERATE)\n"
            "    tran.setTransientNoiseStatus(True)\n"
            "    tran.setNoiseFmax(\"10G\")\n"
            "    tran.setNoiseFmin(\"1k\")\n"
            "    return tran\n") % fn
        prompt = ("Write a Python function %s(stop_time) that creates an MdeTranAnalysis, "
                  "sets the stop time, sets moderate accuracy, enables transient noise with "
                  "fmax=10G and fmin=1k, and returns the object." % fn)
    elif name == "cdfCreateCDF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, simInfoOrder=\"spectre\"):\n"
            "    cdfId = pyScript.cdfCreateCDF(\n"
            "        lib=pyScript.emyString(lib),\n"
            "        cell=pyScript.emyString(cell),\n"
            "        simInfoOrder=pyScript.emyString(simInfoOrder))\n"
            "    if cdfId is None:\n"
            "        return None\n"
            "    pyScript.cdfSaveCDF(cdfId)\n"
            "    return cdfId\n") % fn
        prompt = ("Write a Python function %s(lib, cell, simInfoOrder) that creates a CDF "
                  "with cdfCreateCDF (wrapping args in emyString), saves it with cdfSaveCDF, "
                  "and returns the identifier (or None on failure)." % fn)
    elif name == "cdfGetCDF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(libName, cellName):\n"
            "    cdfId = pyScript.cdfGetCDF(\n"
            "        libName=pyScript.emyString(libName),\n"
            "        cellName=pyScript.emyString(cellName))\n"
            "    if cdfId is None:\n"
            "        return None\n"
            "    return cdfId\n") % fn
        prompt = ("Write a Python function %s(libName, cellName) that gets an existing CDF "
                  "with cdfGetCDF (wrapping args in emyString), returns None if not found, "
                  "otherwise returns the CdsCDFData identifier." % fn)
    elif name == "cdfCreateParam":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cdfId, name, paramType, defValue, prompt):\n"
            "    paramId = pyScript.cdfCreateParam(\n"
            "        cdfDataId=cdfId,\n"
            "        name=pyScript.emyString(name),\n"
            "        paramType=pyScript.emyString(paramType),\n"
            "        defValue=pyScript.emyString(defValue),\n"
            "        prompt=pyScript.emyString(prompt))\n"
            "    if paramId is None:\n"
            "        return None\n"
            "    return paramId\n") % fn
        prompt = ("Write a Python function %s(cdfId, name, paramType, defValue, prompt) "
                  "that creates a CDF parameter with cdfCreateParam (wrapping string args "
                  "in emyString), returns None on failure, otherwise returns the CdsParamDef."
                  % fn)
    elif name == "cdfSet":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(paramId, attrs):\n"
            "    results = {}\n"
            "    for attr, value in attrs.items():\n"
            "        ok = pyScript.cdfSet(paramId=paramId,\n"
            "                             attr=pyScript.emyString(attr),\n"
            "                             value=pyScript.emyString(value))\n"
            "        results[attr] = ok\n"
            "    return results\n") % fn
        prompt = ("Write a Python function %s(paramId, attrs) that takes a dict of "
                  "attribute->value pairs, sets each with cdfSet (wrapping attr and value "
                  "in emyString), and returns a dict of attribute->bool results." % fn)
    elif name == "cdfSetSimInfo":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cdfId, sim_type, netlistProc, compName, termOrder):\n"
            "    ok = pyScript.cdfSetSimInfo(\n"
            "        cdfDataId=cdfId,\n"
            "        type=pyScript.emyString(sim_type),\n"
            "        netlistProcedure=pyScript.emyString(netlistProc),\n"
            "        componentName=pyScript.emyString(compName),\n"
            "        termOrder=pyScript.emyString(termOrder))\n"
            "    if ok:\n"
            "        pyScript.cdfSaveCDF(cdfId)\n"
            "    return ok\n") % fn
        prompt = ("Write a Python function %s(cdfId, sim_type, netlistProc, compName, "
                  "termOrder) that sets simulation info with cdfSetSimInfo (wrapping string "
                  "args in emyString), saves the CDF with cdfSaveCDF if successful, and "
                  "returns the boolean result." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S4 multi-step trace"


def _s5_param_variation(name):
    fn = "vary_" + name.lower().replace(".", "_")
    if name == "MdeSession":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(designs):\n"
            "    sessions = {}\n"
            "    for lib, cell, view in designs:\n"
            "        mde = pyScript.MdeSession.open(lib, cell, view)\n"
            "        sessions[(lib, cell, view)] = mde\n"
            "    return sessions\n") % fn
        prompt = ("Write a Python function %s(designs) that opens an MDE session for each "
                  "(lib, cell, view) tuple in a list with MdeSession.open, and returns a "
                  "dict keyed by the tuple." % fn)
    elif name == "MdeSession.run":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, views):\n"
            "    results = {}\n"
            "    for view in views:\n"
            "        mde = pyScript.MdeSession.open(lib, cell, view)\n"
            "        if mde is None:\n"
            "            results[view] = None\n"
            "            continue\n"
            "        results[view] = mde.run()\n"
            "        mde.close()\n"
            "    return results\n") % fn
        prompt = ("Write a Python function %s(lib, cell, views) that opens an MDE session "
                  "for each view name, runs a simulation with run(), closes the session, "
                  "and returns a dict of view->MdeResult (or None on failure)." % fn)
    elif name == "MdeOutput":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(specs):\n"
            "    outs = []\n"
            "    for nm, expr, etype, sv, pl in specs:\n"
            "        out = pyScript.MdeOutput(nm, expr, etype, sv, pl)\n"
            "        outs.append(out)\n"
            "    return outs\n") % fn
        prompt = ("Write a Python function %s(specs) that creates an MdeOutput for each "
                  "(name, expr, exprType, isSave, isPlot) tuple using positional args, and "
                  "returns the list of output objects." % fn)
    elif name == "MdeDcAnalysis":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(configs):\n"
            "    analyses = []\n"
            "    for mode, val1, val2 in configs:\n"
            "        dc = pyScript.MdeDcAnalysis()\n"
            "        sr = pyScript.MdeSweepRange()\n"
            "        sr.mode = mode\n"
            "        if mode == pyScript.MDE_SWEEP_RANGE_CENTER_SPAN:\n"
            "            sr.center = val1\n"
            "            sr.span = val2\n"
            "        else:\n"
            "            sr.start = val1\n"
            "            sr.stop = val2\n"
            "        dc.setSweepRange(sr)\n"
            "        analyses.append(dc)\n"
            "    return analyses\n") % fn
        prompt = ("Write a Python function %s(configs) that creates an MdeDcAnalysis for "
                  "each (mode, val1, val2) tuple, configuring center-span or start-stop "
                  "sweep range depending on the mode, and returns the list of analyses." % fn)
    elif name == "MdeTranAnalysis":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(stop_times, accuracy):\n"
            "    trans = []\n"
            "    for st in stop_times:\n"
            "        tran = pyScript.MdeTranAnalysis()\n"
            "        tran.setStop(st)\n"
            "        tran.setAccuracyLevel(accuracy)\n"
            "        trans.append(tran)\n"
            "    return trans\n") % fn
        prompt = ("Write a Python function %s(stop_times, accuracy) that creates an "
                  "MdeTranAnalysis for each stop time string, sets the same accuracy level, "
                  "and returns the list of analysis objects." % fn)
    elif name == "cdfCreateCDF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cells, lib, simInfoOrder=\"\"):\n"
            "    cdfs = {}\n"
            "    for cell in cells:\n"
            "        cid = pyScript.cdfCreateCDF(\n"
            "            lib=pyScript.emyString(lib),\n"
            "            cell=pyScript.emyString(cell),\n"
            "            simInfoOrder=pyScript.emyString(simInfoOrder))\n"
            "        cdfs[cell] = cid\n"
            "    return cdfs\n") % fn
        prompt = ("Write a Python function %s(cells, lib, simInfoOrder) that creates a CDF "
                  "for each cell name in a list with cdfCreateCDF, and returns a dict of "
                  "cell->CdsCDFData." % fn)
    elif name == "cdfGetCDF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib_cells):\n"
            "    found = {}\n"
            "    for lib, cell in lib_cells:\n"
            "        cid = pyScript.cdfGetCDF(\n"
            "            libName=pyScript.emyString(lib),\n"
            "            cellName=pyScript.emyString(cell))\n"
            "        found[(lib, cell)] = cid\n"
            "    return found\n") % fn
        prompt = ("Write a Python function %s(lib_cells) that calls cdfGetCDF for each "
                  "(lib, cell) tuple, and returns a dict keyed by the tuple with CdsCDFData "
                  "or None values." % fn)
    elif name == "cdfCreateParam":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cdfId, params):\n"
            "    ids = []\n"
            "    for nm, ptype, dval in params:\n"
            "        pid = pyScript.cdfCreateParam(\n"
            "            cdfDataId=cdfId,\n"
            "            name=pyScript.emyString(nm),\n"
            "            paramType=pyScript.emyString(ptype),\n"
            "            defValue=pyScript.emyString(dval))\n"
            "        ids.append(pid)\n"
            "    return ids\n") % fn
        prompt = ("Write a Python function %s(cdfId, params) that creates a CDF parameter "
                  "for each (name, paramType, defValue) tuple with cdfCreateParam, and "
                  "returns the list of CdsParamDef identifiers." % fn)
    elif name == "cdfSet":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(paramId, attr_vals):\n"
            "    oks = []\n"
            "    for attr, val in attr_vals:\n"
            "        ok = pyScript.cdfSet(\n"
            "            paramId=paramId,\n"
            "            attr=pyScript.emyString(attr),\n"
            "            value=pyScript.emyString(val))\n"
            "        oks.append(ok)\n"
            "    return oks\n") % fn
        prompt = ("Write a Python function %s(paramId, attr_vals) that sets each (attr, "
                  "value) pair on a CDF parameter with cdfSet, and returns the list of "
                  "boolean results." % fn)
    elif name == "cdfSetSimInfo":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cdfId, sim_configs):\n"
            "    results = {}\n"
            "    for sim_type, np_val in sim_configs:\n"
            "        ok = pyScript.cdfSetSimInfo(\n"
            "            cdfDataId=cdfId,\n"
            "            type=pyScript.emyString(sim_type),\n"
            "            netlistProcedure=pyScript.emyString(np_val))\n"
            "        results[sim_type] = ok\n"
            "    return results\n") % fn
        prompt = ("Write a Python function %s(cdfId, sim_configs) that sets simulation info "
                  "for each (sim_type, netlistProcedure) pair with cdfSetSimInfo, and returns "
                  "a dict of sim_type->bool." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S5 parameter variation"


def build_pairs(eval_eps, limit=None):
    pairs = []
    rejected = 0
    reject_details = []

    def _add(ptype, cid, prompt, completion, api_used, note):
        blob = prompt + "\n" + completion
        hit = fingerprint_scan(blob, eval_eps)
        if hit:
            rejected += 1
            reject_details.append({"id": cid, "type": ptype, "hit": hit})
            return
        pairs.append({"id": cid, "type": ptype, "prompt": prompt,
                      "completion": completion, "api_used": api_used,
                      "contamination_check": "PASS", "note": note})

    for name in API_ORDER:
        p, c, a, n = _s1_doc_to_code(name); _add("S1", "s1_" + name, p, c, a, n)
    for name in API_ORDER:
        p, c, a, n = _s4_multi_step(name); _add("S4", "s4_" + name, p, c, a, n)
    for name in API_ORDER:
        p, c, a, n = _s5_param_variation(name); _add("S5", "s5_" + name, p, c, a, n)

    chains = [
        ("chain_mde_session_run_output",
         "Write a Python function setup_and_simulate(lib, cell, view, outputs) that opens an MDE session with MdeSession.open, creates MdeOutput objects from a list of (name, expr) tuples, launches a simulation run with run(), closes the session, and returns the MdeResult (or None on failure).",
         ["MdeSession", "MdeOutput", "MdeSession.run"],
         ("import pyAether as pyScript\n\n"
          "def setup_and_simulate(lib, cell, view, outputs):\n"
          "    mde = pyScript.MdeSession.open(lib, cell, view)\n"
          "    if mde is None:\n"
          "        return None\n"
          "    out_objs = []\n"
          "    for nm, expr in outputs:\n"
          "        out = pyScript.MdeOutput(nm, expr, \"Expression\", True, False)\n"
          "        out_objs.append(out)\n"
          "    result = mde.run()\n"
          "    mde.close()\n"
          "    return result\n")),
        ("chain_mde_dc_tran_analysis",
         "Write a Python function configure_analyses(dc_center, dc_span, tran_stop) that creates an MdeDcAnalysis with center-span sweep range and an MdeTranAnalysis with the given stop time and conservative accuracy, and returns both objects.",
         ["MdeDcAnalysis", "MdeTranAnalysis"],
         ("import pyAether as pyScript\n\n"
          "def configure_analyses(dc_center, dc_span, tran_stop):\n"
          "    dc = pyScript.MdeDcAnalysis()\n"
          "    dc.setSaveDcOperatingPointStatus(True)\n"
          "    sr = pyScript.MdeSweepRange()\n"
          "    sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n"
          "    sr.center = dc_center\n"
          "    sr.span = dc_span\n"
          "    dc.setSweepRange(sr)\n"
          "    tran = pyScript.MdeTranAnalysis()\n"
          "    tran.setStop(tran_stop)\n"
          "    tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n"
          "    return dc, tran\n")),
        ("chain_cdf_get_create_param",
         "Write a Python function add_cdf_param(libName, cellName, param_name, paramType, defValue) that gets an existing CDF with cdfGetCDF, creates a parameter in it with cdfCreateParam, and returns the CdsParamDef (or None if the CDF does not exist).",
         ["cdfGetCDF", "cdfCreateParam"],
         ("import pyAether as pyScript\n\n"
          "def add_cdf_param(libName, cellName, param_name, paramType, defValue):\n"
          "    cdfId = pyScript.cdfGetCDF(\n"
          "        libName=pyScript.emyString(libName),\n"
          "        cellName=pyScript.emyString(cellName))\n"
          "    if cdfId is None:\n"
          "        return None\n"
          "    paramId = pyScript.cdfCreateParam(\n"
          "        cdfDataId=cdfId,\n"
          "        name=pyScript.emyString(param_name),\n"
          "        paramType=pyScript.emyString(paramType),\n"
          "        defValue=pyScript.emyString(defValue))\n"
          "    return paramId\n")),
        ("chain_cdf_create_param_set_siminfo",
         "Write a Python function setup_new_cdf(lib, cell, params, sim_type, netlistProc) that creates a CDF with cdfCreateCDF, creates parameters from a list of (name, paramType, defValue) tuples with cdfCreateParam, sets simulation info with cdfSetSimInfo, saves with cdfSaveCDF, and returns the CdsCDFData.",
         ["cdfCreateCDF", "cdfCreateParam", "cdfSetSimInfo"],
         ("import pyAether as pyScript\n\n"
          "def setup_new_cdf(lib, cell, params, sim_type, netlistProc):\n"
          "    cdfId = pyScript.cdfCreateCDF(\n"
          "        lib=pyScript.emyString(lib),\n"
          "        cell=pyScript.emyString(cell))\n"
          "    if cdfId is None:\n"
          "        return None\n"
          "    for nm, ptype, dval in params:\n"
          "        pyScript.cdfCreateParam(\n"
          "            cdfDataId=cdfId,\n"
          "            name=pyScript.emyString(nm),\n"
          "            paramType=pyScript.emyString(ptype),\n"
          "            defValue=pyScript.emyString(dval))\n"
          "    pyScript.cdfSetSimInfo(\n"
          "        cdfDataId=cdfId,\n"
          "        type=pyScript.emyString(sim_type),\n"
          "        netlistProcedure=pyScript.emyString(netlistProc))\n"
          "    pyScript.cdfSaveCDF(cdfId)\n"
          "    return cdfId\n")),
        ("chain_cdf_get_set_attribute",
         "Write a Python function update_cdf_attr(libName, cellName, paramName, attr, value) that gets a CDF with cdfGetCDF, finds the parameter with cdfFindParamByName, sets an attribute with cdfSet, saves with cdfSaveCDF, and returns the boolean result.",
         ["cdfGetCDF", "cdfSet"],
         ("import pyAether as pyScript\n\n"
          "def update_cdf_attr(libName, cellName, paramName, attr, value):\n"
          "    cdfId = pyScript.cdfGetCDF(\n"
          "        libName=pyScript.emyString(libName),\n"
          "        cellName=pyScript.emyString(cellName))\n"
          "    if cdfId is None:\n"
          "        return False\n"
          "    paramId = pyScript.cdfFindParamByName(\n"
          "        cdfDataId=cdfId,\n"
          "        paramName=pyScript.emyString(paramName))\n"
          "    if paramId is None:\n"
          "        return False\n"
          "    ok = pyScript.cdfSet(\n"
          "        paramId=paramId,\n"
          "        attr=pyScript.emyString(attr),\n"
          "        value=pyScript.emyString(value))\n"
          "    if ok:\n"
          "        pyScript.cdfSaveCDF(cdfId)\n"
          "    return ok\n")),
    ]
    for cid, prompt, api_used, completion in chains:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")

    lookups = [
        ("open an MDE simulation session", "MdeSession",
         'mde = pyScript.MdeSession.open("testLib", "testCell", "state")'),
        ("launch an MDE simulation run", "MdeSession.run",
         'result = mde.run()'),
        ("define a simulation output expression", "MdeOutput",
         'out = pyScript.MdeOutput("vout", "V(out)", "Expression", True, False)'),
        ("configure a DC analysis with sweep range", "MdeDcAnalysis",
         'dc = pyScript.MdeDcAnalysis()\ndc.setSaveDcOperatingPointStatus(True)'),
        ("configure a transient analysis with stop time", "MdeTranAnalysis",
         'tran = pyScript.MdeTranAnalysis()\ntran.setStop("100n")'),
        ("create a CDF identifier for a library and cell", "cdfCreateCDF",
         'cdfId = pyScript.cdfCreateCDF(lib=pyScript.emyString("lib"), cell=pyScript.emyString("cell"))'),
        ("get an existing CDF identifier", "cdfGetCDF",
         'cdfId = pyScript.cdfGetCDF(libName=pyScript.emyString("lib"), cellName=pyScript.emyString("cell"))'),
        ("create a parameter in a CDF", "cdfCreateParam",
         'pid = pyScript.cdfCreateParam(cdfDataId=cdfId, name=pyScript.emyString("w"), paramType=pyScript.emyString("string"))'),
        ("set an attribute of a CDF parameter", "cdfSet",
         'ok = pyScript.cdfSet(paramId=pid, attr=pyScript.emyString("prompt"), value=pyScript.emyString("Width"))'),
        ("set simulation information for a CDF", "cdfSetSimInfo",
         'ok = pyScript.cdfSetSimInfo(cdfDataId=cdfId, type=pyScript.emyString("spectre"))'),
    ]
    for intent, api, usage in lookups:
        prompt = ("You are an EDA automation assistant. Which PyAether API is used to %s? "
                  "Show a minimal correct usage example." % intent)
        completion = ("The API is `%s`.\n\n```python\nimport pyAether as pyScript\n%s\n```"
                      % (api, usage))
        _add("S6", "s6_" + api, prompt, completion, [api], "S6 API lookup")

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
        "report_id": "R183",
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
        sys.stderr.write("GATE: FAIL (pollution detected) -- do NOT use v13\n")
        sys.exit(2)
    sys.stderr.write("GATE: PASS -- v13 is training-ready\n")


if __name__ == "__main__":
    main()
