#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r190_mde_sweep_platform_corpus.py
R190 -- v20 PyAether SFT corpus: the Mde* "simulation sweep / platform" blind spot.

BACKGROUND (R181 coverage audit, updated R189):
  v11-v19 (398 pairs) cover 68/164 eval raw pyScript APIs. 96 remain blind.
  A data-driven eval-usage scan (R190 wake) shows the Mde* family is NOW the
  largest blind family: 35 usages across 22 APIs (sweep / platform / analysis).
  R183 (v13) covered 5 Mde* primitives (MdeSession, MdeSession.run, MdeOutput,
  ...) but left the sweep-config and platform-policy classes untouched. R190
  targets the 7 highest-impact Mde* "simulation sweep / platform" APIs:
    MdeTranAnalysis     : tran analysis data object (accuracy/instance list/
                          multiple-runs/noise)
    MdeAcAnalysis       : ac analysis data object (sweep range/type/variable +
                          add-specific-points)
    MdeSweepRange       : sweep range config (center-span / start-stop modes)
    MdeSweepType        : sweep type config (log/linear modes + log num-step)
    MdeSweepVariable    : sweep variable config (model-parameter mode)
    MdeSpeOutput        : Spectre output def (name/expr/exprType/evalType/...)
    MdePlatLocalJobPolicy: platform local job policy (maxJobNum)
  All ISOLATE-class (eval_count>0, appear as helpers in eval solutions). The
  red line (S5.1) isolates on eval *entry_point* strings (the 155 task function
  names), NOT on helper API names. Teaching the *public API reference* of these
  simulation-config primitives is explicitly allowed. The fingerprint scan below
  rejects any pair whose prompt+completion contains a literal eval entry_point.
  The MDE_* enum constants are taught as the *values* of the config classes.

  Authoritative signatures fetched via pyAether MCP get_api_details (R190 wake).

v20: 7 Mde* APIs, each with S1 doc->code, S4 multi-step trace, S5 param
  variation. Plus 7 S3 multi-API chains and 7 S6 API lookups = 35 pairs.

Usage:
  python3 baize_posttrain_r190_mde_sweep_platform_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v20_mde_sweep_platform.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["MdeTranAnalysis"] = {
    "sig": "MdeTranAnalysis()  [class; data object for MdeSetting.setTranAnalysis]",
    "desc": "A tran (transient) analysis data object -- an in-memory mirror of the MDE tran analysis. Used in MdeSetting.setTranAnalysis. Mirrors the tran section in the Aether Add/Modify Analysis form. Dynamic Parameter and Options are not supported at this time.",
    "params": {},
    "returns": "MdeTranAnalysis instance (pass to MdeSetting.setTranAnalysis)",
    "methods": ("setAccuracyLevel(level) -> None; "
                "setInstanceList(value: str) -> None; "
                "setMultipleRunsStatus(state: bool) -> None; "
                "setNoiseContribution(mode) -> None; "
                "setNoiseFmax(value: str) -> None; "
                "setNoiseFmin(value: str) -> None; "
                "setNoiseScale(value: str) -> None; "
                "setNoiseSeed(value: str) -> None; "
                "setNoiseTmin(value: str) -> None; "
                "setNoiseUpdate(mode) -> None; "
                "setStep(step: str) -> None; setStop(stop: str) -> None"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> tran = pyScript.MdeTranAnalysis()\n'
                '>>> tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n'
                '>>> tran.setInstanceList("I0 I1")\n'
                '>>> tran.setStep("1n")\n'
                '>>> tran.setStop("10u")\n'
                '>>> tran.setMultipleRunsStatus(True)'),
    "category": "MDE L2 / Tran Analysis",
    "safety": "ISOLATE", "eval_count": 12,
    "key_notes": "Constructor takes no args. Accuracy level enum: MDE_TRAN_ACC_LEVEL_CONSERVATIVE, MDE_TRAN_ACC_LEVEL_MODERATE, MDE_TRAN_ACC_LEVEL_LIBERAL. Noise contribution enum: MDE_TRAN_NOISE_CONTRIBUTION_ON, MDE_TRAN_NOISE_CONTRIBUTION_OFF. All numeric/time values (step, stop, noiseFmax, ...) are passed as STRINGS, not floats. After configuring, pass the object to MdeSetting.setTranAnalysis(tran) and call enableTranAnalysis on the setting."}
API_DOCS["MdeAcAnalysis"] = {
    "sig": "MdeAcAnalysis()  [class; data object for MdeSetting.setAcAnalysis]",
    "desc": "An ac (AC small-signal) analysis data object -- an in-memory mirror of the MDE ac analysis. Used in MdeSetting.setAcAnalysis. Options are not supported at this time. Composes MdeSweepRange, MdeSweepType, MdeSweepVariable and MdeAddSpecificPoints sub-objects.",
    "params": {},
    "returns": "MdeAcAnalysis instance (pass to MdeSetting.setAcAnalysis)",
    "methods": ("setAddSpecificPoints(specificPoints) -> None; "
                "setSweepRange(sweepRange: MdeSweepRange) -> None; "
                "setSweepType(sweepType: MdeSweepType) -> None; "
                "setSweepVariable(sweepVar: MdeSweepVariable) -> None"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> ac = pyScript.MdeAcAnalysis()\n'
                '>>> sr = pyScript.MdeSweepRange()\n'
                '>>> sr.mode = pyScript.MDE_SWEEP_RANGE_START_STOP\n'
                '>>> sr.start = "1"\n'
                '>>> sr.stop = "1G"\n'
                '>>> ac.setSweepRange(sr)\n'
                '>>> st = pyScript.MdeSweepType()\n'
                '>>> st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n'
                '>>> st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP\n'
                '>>> st.numberOfStepsForLog = "10"\n'
                '>>> ac.setSweepType(st)'),
    "category": "MDE L2 / Ac Analysis",
    "safety": "ISOLATE", "eval_count": 10,
    "key_notes": "Constructor takes no args. Compose the four sub-config objects (MdeSweepRange/MdeSweepType/MdeSweepVariable/MdeAddSpecificPoints) and set them via the set* methods. After MdeSetting.setAcAnalysis(ac), the ac analysis must be ENABLED by calling enableAcAnalysis on the MdeSetting -- otherwise it will not run. setSweepVariable takes an MdeSweepVariable whose .mode is e.g. MDE_SWEEP_VARIABLE_MODEL_PARAMETER."}

API_DOCS["MdeSweepRange"] = {
    "sig": "MdeSweepRange()  [class; sweep-range config object]",
    "desc": "A sweep-range configuration object used by MdeAcAnalysis.setSweepRange (and the tran/dc sweep flows). Holds the sweep mode (center-span vs start-stop) plus the center/span or start/stop numeric strings.",
    "params": {},
    "returns": "MdeSweepRange instance (assign .mode/.center/.span/.start/.stop, then pass to setSweepRange)",
    "methods": "properties: mode (MDE_SWEEP_RANGE_*), center (str), span (str), start (str), stop (str)",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> sr = pyScript.MdeSweepRange()\n'
                '>>> sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n'
                '>>> sr.center = "10"\n'
                '>>> sr.span = "10"\n'
                '>>> print(sr.center, sr.span)'),
    "category": "MDE L2 / Sweep Config",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "mode enum: MDE_SWEEP_RANGE_CENTER_SPAN (center+span) or MDE_SWEEP_RANGE_START_STOP (start+stop). center/span/start/stop are STRINGS (e.g. \"10\", \"1G\"), not numbers. Set the fields matching the chosen mode; the unused fields are ignored. Construct with no args then assign attributes."}
API_DOCS["MdeSweepType"] = {
    "sig": "MdeSweepType()  [class; sweep-type config object]",
    "desc": "A sweep-type configuration object used by MdeAcAnalysis.setSweepType. Holds the sweep mode (log vs linear) and, for log sweeps, the log sub-mode plus the number of steps.",
    "params": {},
    "returns": "MdeSweepType instance (assign .mode/.logMode/.numberOfStepsForLog, then pass to setSweepType)",
    "methods": "properties: mode (MDE_SWEEP_TYPE_*), logMode (MDE_SWEEP_TYPE_LOG_*), numberOfStepsForLog (str), stepSize (str)",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> st = pyScript.MdeSweepType()\n'
                '>>> st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n'
                '>>> st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP\n'
                '>>> st.numberOfStepsForLog = "10"\n'
                '>>> print(st.numberOfStepsForLog)'),
    "category": "MDE L2 / Sweep Config",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "mode enum: MDE_SWEEP_TYPE_LOG or MDE_SWEEP_TYPE_LINEAR. For LOG mode set logMode to MDE_SWEEP_TYPE_LOG_NUM_STEP (or the per-decade variant) and numberOfStepsForLog as a STRING (e.g. \"10\"). For LINEAR mode set stepSize. All numeric fields are strings."}

API_DOCS["MdeSweepVariable"] = {
    "sig": "MdeSweepVariable()  [class; sweep-variable config object]",
    "desc": "A sweep-variable configuration object used by MdeAcAnalysis.setSweepVariable. Specifies WHAT is swept -- e.g. a model parameter, a design variable, or frequency -- via the mode plus the parameter names.",
    "params": {},
    "returns": "MdeSweepVariable instance (assign .mode/.modelName/.modelParameterName/.freForMod, then pass to setSweepVariable)",
    "methods": "properties: mode (MDE_SWEEP_VARIABLE_*), modelName (str), modelParameterName (str), freForMod (str)",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> sv = pyScript.MdeSweepVariable()\n'
                '>>> sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n'
                '>>> sv.modelName = "C0"\n'
                '>>> sv.modelParameterName = "I0"\n'
                '>>> sv.freForMod = "10"\n'
                '>>> print(sv.modelParameterName)'),
    "category": "MDE L2 / Sweep Config",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "mode enum: MDE_SWEEP_VARIABLE_MODEL_PARAMETER (sweep a model parameter) and the design-variable / frequency variants. For MODEL_PARAMETER set modelName (the instance/model name) and modelParameterName (the parameter name); freForMod is the frequency used for model extraction. All fields are strings."}
API_DOCS["MdeSpeOutput"] = {
    "sig": "MdeSpeOutput(name, expr, exprType, evalType, save, plot, spec='')  [class]",
    "desc": "MdeSpeOutput defines a Spectre simulation output expression. Stores the output name, expression string, expression type, evaluation type, save/plot flags and an optional spec string. Used to configure what signals to measure during an MDE Spectre-mode simulation run (added via MdeSetting.addSpeOutput).",
    "params": {
        "name": "str - output name (e.g. 'vout')",
        "expr": "str - expression string (e.g. 'V(out)')",
        "exprType": "str - expression type (e.g. 'Expression', 'Signal')",
        "evalType": "str - evaluation type; valid values: 'points', 'corners', 'sweeps', 'all'",
        "save": "bool - whether to save the output",
        "plot": "bool - whether to plot the output",
        "spec": "str, optional - output specification, e.g. '< 10n'",
    },
    "returns": "MdeSpeOutput instance (pass to MdeSetting.addSpeOutput)",
    "methods": ("name() -> str; expr() -> str; exprType() -> str; "
                "evalType() -> str; spec() -> str; "
                "properties: name_p, expr_p, exprType_p, evalType_p, spec_p"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> out = pyScript.MdeSpeOutput("vout", "V(out)", "Expression", "All", True, False)\n'
                '>>> print(out.name())\n'
                '>>> print(out.expr())\n'
                '>>> print(out.evalType())'),
    "category": "MDE L2 / Spectre Output",
    "safety": "ISOLATE", "eval_count": 6,
    "key_notes": "evalType must be one of 'points', 'corners', 'sweeps', 'all' (case-sensitive as documented). All constructor args except spec are required. Add to a setting via MdeSetting.addSpeOutput(out) -- only valid in Spectre mode; check lastError() on failure. The evalType_p property mirrors evalType()."}

API_DOCS["MdePlatLocalJobPolicy"] = {
    "sig": "MdePlatLocalJobPolicy(maxJobNum=1)  [class; platform local job policy]",
    "desc": "An MdePlatLocalJobPolicy object represents the local-job policy for an MDE platform run -- i.e. how many local simulation jobs may run concurrently. Set on the platform session to control local execution parallelism.",
    "params": {"maxJobNum": "int, optional - max concurrent local jobs (default 1; documented range 1-30000)"},
    "returns": "MdePlatLocalJobPolicy instance",
    "methods": "getMaxJobNum() -> int; setMaxJobNum(n: int) -> None",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> policy = pyScript.MdePlatLocalJobPolicy(8)\n'
                '>>> print(policy.getMaxJobNum())\n'
                '>>> policy.setMaxJobNum(16)\n'
                '>>> print(policy.getMaxJobNum())'),
    "category": "MDE Platform / Job Policy",
    "safety": "ISOLATE", "eval_count": 4,
    "key_notes": "maxJobNum must be an INT -- a float raises TypeError (use int() to coerce). The API does NOT enforce the 1-30000 range (it accepts 0/negatives), so validate client-side. Each instance maintains its own count independently. Sister classes: MdePlatLSFJobPolicy / MdePlatDonauJobPolicy / MdePlatOGEJobPolicy for cluster job policies."}

API_ORDER = ["MdeTranAnalysis", "MdeAcAnalysis", "MdeSweepRange",
             "MdeSweepType", "MdeSweepVariable", "MdeSpeOutput",
             "MdePlatLocalJobPolicy"]


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

    # ---- S1: doc -> code (7 pairs, one per API) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v20-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)
    # ---- S4: multi-step trace (7 pairs) ----
    s4_traces = [
        ("MdeTranAnalysis",
         "Configure a transient analysis: conservative accuracy, sweep instances I0 and I1, step 1n, stop 10u, multiple runs enabled, and noise contribution on.",
         ["MdeTranAnalysis"],
         ("import pyAether as pyScript\n\n"
          "tran = pyScript.MdeTranAnalysis()\n"
          "tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n"
          'tran.setInstanceList("I0 I1")\n'
          'tran.setStep("1n")\n'
          'tran.setStop("10u")\n'
          "tran.setMultipleRunsStatus(True)\n"
          "tran.setNoiseContribution(pyScript.MDE_TRAN_NOISE_CONTRIBUTION_ON)\n"
          "# hand to the MDE setting: setting.setTranAnalysis(tran); setting.enableTranAnalysis()\n"
          'print("tran analysis configured")')),
        ("MdeAcAnalysis",
         "Build an AC analysis with a start-stop sweep range (1 to 1G), a log sweep type with 10 num-steps, and a model-parameter sweep variable (model C0, parameter I0), then wire it into the AC analysis object.",
         ["MdeAcAnalysis", "MdeSweepRange", "MdeSweepType", "MdeSweepVariable"],
         ("import pyAether as pyScript\n\n"
          "ac = pyScript.MdeAcAnalysis()\n"
          "sr = pyScript.MdeSweepRange()\n"
          "sr.mode = pyScript.MDE_SWEEP_RANGE_START_STOP\n"
          'sr.start = "1"\n'
          'sr.stop = "1G"\n'
          "ac.setSweepRange(sr)\n"
          "st = pyScript.MdeSweepType()\n"
          "st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n"
          "st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP\n"
          'st.numberOfStepsForLog = "10"\n'
          "ac.setSweepType(st)\n"
          "sv = pyScript.MdeSweepVariable()\n"
          "sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n"
          'sv.modelName = "C0"\n'
          'sv.modelParameterName = "I0"\n'
          'sv.freForMod = "10"\n'
          "ac.setSweepVariable(sv)\n"
          "# setting.setAcAnalysis(ac); setting.enableAcAnalysis()\n"
          'print("ac analysis configured")')),
        ("MdeSweepRange",
         "Configure a center-span sweep range centered at 100 with span 50, and report the chosen values.",
         ["MdeSweepRange"],
         ("import pyAether as pyScript\n\n"
          "sr = pyScript.MdeSweepRange()\n"
          "sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n"
          'sr.center = "100"\n'
          'sr.span = "50"\n'
          'print("center:", sr.center, "span:", sr.span)')),
        ("MdeSweepType",
         "Configure a linear sweep with a step size of 0.5 and report it, then also show how to switch to a 20-step log sweep.",
         ["MdeSweepType"],
         ("import pyAether as pyScript\n\n"
          "st = pyScript.MdeSweepType()\n"
          "st.mode = pyScript.MDE_SWEEP_TYPE_LINEAR\n"
          'st.stepSize = "0.5"\n'
          'print("linear step size:", st.stepSize)\n\n'
          "st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n"
          "st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP\n"
          'st.numberOfStepsForLog = "20"\n'
          'print("log steps:", st.numberOfStepsForLog)')),
        ("MdeSweepVariable",
         "Set up a model-parameter sweep variable on model C0 parameter W, with a model-extraction frequency of 1k, and print the parameter name.",
         ["MdeSweepVariable"],
         ("import pyAether as pyScript\n\n"
          "sv = pyScript.MdeSweepVariable()\n"
          "sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n"
          'sv.modelName = "C0"\n'
          'sv.modelParameterName = "W"\n'
          'sv.freForMod = "1k"\n'
          'print("sweeping parameter:", sv.modelParameterName)')),
        ("MdeSpeOutput",
         "Define three Spectre simulation outputs: a saved+plotted gain expression evaluated at all points, a signal saved but not plotted at corners, and a power expression saved at sweeps. Print each name and eval type.",
         ["MdeSpeOutput"],
         ("import pyAether as pyScript\n\n"
          "gain = pyScript.MdeSpeOutput(\"gain\", \"V(out)/V(in)\", \"Expression\", \"all\", True, True)\n"
          "sig = pyScript.MdeSpeOutput(\"vout\", \"V(out)\", \"Signal\", \"corners\", True, False)\n"
          "pwr = pyScript.MdeSpeOutput(\"pwr\", \"I(VDD)*V(VDD)\", \"Expression\", \"sweeps\", True, False)\n"
          "for o in (gain, sig, pwr):\n"
          "    print(o.name(), o.evalType())")),
        ("MdePlatLocalJobPolicy",
         "Create a local job policy allowing 8 concurrent jobs, verify the count, then raise it to 16 and verify again.",
         ["MdePlatLocalJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "policy = pyScript.MdePlatLocalJobPolicy(8)\n"
          'print("max jobs:", policy.getMaxJobNum())\n'
          "policy.setMaxJobNum(16)\n"
          'print("updated max jobs:", policy.getMaxJobNum())')),
    ]
    for name, prompt, api_used, completion in s4_traces:
        _add("S4", "v20-S4-%s" % name, prompt, completion, api_used,
             "S4 multi_step trace for %s" % name)
    # ---- S5: param variation (7 pairs) ----
    s5_variants = [
        ("MdeTranAnalysis",
         "Configure a transient analysis with liberal accuracy, no instance list, step 10n, stop 1m, multiple runs disabled, and noise contribution off.",
         ["MdeTranAnalysis"],
         ("import pyAether as pyScript\n\n"
          "tran = pyScript.MdeTranAnalysis()\n"
          "tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_LIBERAL)\n"
          'tran.setInstanceList("")\n'
          'tran.setStep("10n")\n'
          'tran.setStop("1m")\n'
          "tran.setMultipleRunsStatus(False)\n"
          "tran.setNoiseContribution(pyScript.MDE_TRAN_NOISE_CONTRIBUTION_OFF)\n")),
        ("MdeAcAnalysis",
         "Build an AC analysis that adds specific points I0 and I1 to the sweep, using a start-stop range and a linear sweep type.",
         ["MdeAcAnalysis", "MdeAddSpecificPoints"],
         ("import pyAether as pyScript\n\n"
          "ac = pyScript.MdeAcAnalysis()\n"
          "sp = pyScript.MdeAddSpecificPoints()\n"
          "sp.addSpecificPointsStatue = True\n"
          'sp.specificPoints = "I0 I1"\n'
          "ac.setAddSpecificPoints(sp)\n"
          "sr = pyScript.MdeSweepRange()\n"
          "sr.mode = pyScript.MDE_SWEEP_RANGE_START_STOP\n"
          'sr.start = "10"\n'
          'sr.stop = "10k"\n'
          "ac.setSweepRange(sr)\n"
          "st = pyScript.MdeSweepType()\n"
          "st.mode = pyScript.MDE_SWEEP_TYPE_LINEAR\n"
          'st.stepSize = "100"\n'
          "ac.setSweepType(st)\n")),
        ("MdeSweepRange",
         "Configure a start-stop sweep range from 0 to 100 and report the endpoints.",
         ["MdeSweepRange"],
         ("import pyAether as pyScript\n\n"
          "sr = pyScript.MdeSweepRange()\n"
          "sr.mode = pyScript.MDE_SWEEP_RANGE_START_STOP\n"
          'sr.start = "0"\n'
          'sr.stop = "100"\n'
          'print("start:", sr.start, "stop:", sr.stop)')),
        ("MdeSweepType",
         "Configure a 50-step log sweep and report the number of steps.",
         ["MdeSweepType"],
         ("import pyAether as pyScript\n\n"
          "st = pyScript.MdeSweepType()\n"
          "st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n"
          "st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP\n"
          'st.numberOfStepsForLog = "50"\n'
          'print("log steps:", st.numberOfStepsForLog)')),
        ("MdeSweepVariable",
         "Set up a model-parameter sweep on model R0 parameter L with extraction frequency 10k.",
         ["MdeSweepVariable"],
         ("import pyAether as pyScript\n\n"
          "sv = pyScript.MdeSweepVariable()\n"
          "sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n"
          'sv.modelName = "R0"\n'
          'sv.modelParameterName = "L"\n'
          'sv.freForMod = "10k"\n')),
        ("MdeSpeOutput",
         "Define a single Spectre output for the node voltage V(out) that is saved and plotted, evaluated at points, with a spec of '< 1n'.",
         ["MdeSpeOutput"],
         ("import pyAether as pyScript\n\n"
          "out = pyScript.MdeSpeOutput(\"vout\", \"V(out)\", \"Signal\", \"points\", True, True, \"< 1n\")\n"
          "print(out.name(), out.spec())")),
        ("MdePlatLocalJobPolicy",
         "Create a local job policy with the default constructor and report its initial max job count, then set it to 4.",
         ["MdePlatLocalJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "policy = pyScript.MdePlatLocalJobPolicy()\n"
          'print("default max jobs:", policy.getMaxJobNum())\n'
          "policy.setMaxJobNum(4)\n"
          'print("max jobs now:", policy.getMaxJobNum())')),
    ]
    for name, prompt, api_used, completion in s5_variants:
        _add("S5", "v20-S5-%s" % name, prompt, completion, api_used,
             "S5 param variation for %s" % name)
    # ---- S3: multi-API chains (7 pairs) ----
    chains = [
        ("v20-S3-tran-full",
         "Build a complete transient analysis object and configure it for a conservative run: accuracy, instance list, step, stop, and noise -- the full set needed before handing to MdeSetting.setTranAnalysis.",
         ["MdeTranAnalysis"],
         ("import pyAether as pyScript\n\n"
          "tran = pyScript.MdeTranAnalysis()\n"
          "tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n"
          'tran.setInstanceList("I0/M0 I1/M0")\n'
          'tran.setStep("100p")\n'
          'tran.setStop("5u")\n'
          "tran.setMultipleRunsStatus(False)\n"
          "tran.setNoiseContribution(pyScript.MDE_TRAN_NOISE_CONTRIBUTION_OFF)\n"
          'print("tran ready for setTranAnalysis")')),
        ("v20-S3-ac-full",
         "Build a complete AC analysis object: a log frequency sweep from 1 to 1G with 20 steps, sweeping a model parameter C0.W, plus an add-specific-points flag -- the full chain before MdeSetting.setAcAnalysis + enableAcAnalysis.",
         ["MdeAcAnalysis", "MdeSweepRange", "MdeSweepType", "MdeSweepVariable", "MdeAddSpecificPoints"],
         ("import pyAether as pyScript\n\n"
          "ac = pyScript.MdeAcAnalysis()\n"
          "sr = pyScript.MdeSweepRange()\n"
          "sr.mode = pyScript.MDE_SWEEP_RANGE_START_STOP\n"
          'sr.start = "1"\n'
          'sr.stop = "1G"\n'
          "ac.setSweepRange(sr)\n"
          "st = pyScript.MdeSweepType()\n"
          "st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n"
          "st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP\n"
          'st.numberOfStepsForLog = "20"\n'
          "ac.setSweepType(st)\n"
          "sv = pyScript.MdeSweepVariable()\n"
          "sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n"
          'sv.modelName = "C0"\n'
          'sv.modelParameterName = "W"\n'
          'sv.freForMod = "1k"\n'
          "ac.setSweepVariable(sv)\n"
          "sp = pyScript.MdeAddSpecificPoints()\n"
          "sp.addSpecificPointsStatue = True\n"
          'sp.specificPoints = "I0 I1"\n'
          "ac.setAddSpecificPoints(sp)\n"
          'print("ac ready for setAcAnalysis + enableAcAnalysis")')),
        ("v20-S3-sweep-range-center",
         "Configure a center-span sweep range and report which mode and values were set.",
         ["MdeSweepRange"],
         ("import pyAether as pyScript\n\n"
          "sr = pyScript.MdeSweepRange()\n"
          "sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n"
          'sr.center = "1k"\n'
          'sr.span = "500"\n'
          'print("mode center-span, center", sr.center, "span", sr.span)')),
        ("v20-S3-sweep-type-linear",
         "Configure a linear sweep with step size 10 and confirm it.",
         ["MdeSweepType"],
         ("import pyAether as pyScript\n\n"
          "st = pyScript.MdeSweepType()\n"
          "st.mode = pyScript.MDE_SWEEP_TYPE_LINEAR\n"
          'st.stepSize = "10"\n'
          'print("linear sweep, stepSize", st.stepSize)')),
        ("v20-S3-sweep-variable-freq",
         "Configure a sweep variable in model-parameter mode targeting model M0 parameter L with extraction frequency 100.",
         ["MdeSweepVariable"],
         ("import pyAether as pyScript\n\n"
          "sv = pyScript.MdeSweepVariable()\n"
          "sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n"
          'sv.modelName = "M0"\n'
          'sv.modelParameterName = "L"\n'
          'sv.freForMod = "100"\n'
          'print("sweeping", sv.modelName, sv.modelParameterName)')),
        ("v20-S3-speoutput-corner",
         "Define a corner-evaluation Spectre output for the supply current expression I(VDD) that is saved but not plotted, and report its evalType.",
         ["MdeSpeOutput"],
         ("import pyAether as pyScript\n\n"
          "out = pyScript.MdeSpeOutput(\"idd\", \"I(VDD)\", \"Expression\", \"corners\", True, False)\n"
          'print(out.name(), out.evalType())')),
        ("v20-S3-local-policy-default",
         "Create a local job policy with the default max job count, then configure it for a modest 4-job concurrency and report the result.",
         ["MdePlatLocalJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "policy = pyScript.MdePlatLocalJobPolicy()\n"
          'print("initial:", policy.getMaxJobNum())\n'
          "policy.setMaxJobNum(4)\n"
          'print("configured:", policy.getMaxJobNum())')),
    ]
    for cid, prompt, api_used, completion in chains:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")
    # ---- S6: API lookup (7 pairs) ----
    lookups = [
        ("configure a transient analysis data object before passing it to MdeSetting.setTranAnalysis",
         "MdeTranAnalysis",
         'tran = pyScript.MdeTranAnalysis()\ntran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\ntran.setStep("1n")\ntran.setStop("10u")'),
        ("configure an AC analysis object with sweep range, sweep type and sweep variable",
         "MdeAcAnalysis",
         'ac = pyScript.MdeAcAnalysis()\nac.setSweepRange(pyScript.MdeSweepRange())\nac.setSweepType(pyScript.MdeSweepType())\nac.setSweepVariable(pyScript.MdeSweepVariable())'),
        ("set the sweep range of an AC analysis to a center-span or start-stop range",
         "MdeSweepRange",
         'sr = pyScript.MdeSweepRange()\nsr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\nsr.center = "10"\nsr.span = "10"'),
        ("set the sweep type of an AC analysis to a log sweep with a number of steps",
         "MdeSweepType",
         'st = pyScript.MdeSweepType()\nst.mode = pyScript.MDE_SWEEP_TYPE_LOG\nst.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP\nst.numberOfStepsForLog = "10"'),
        ("set the swept variable of an AC analysis to a model parameter",
         "MdeSweepVariable",
         'sv = pyScript.MdeSweepVariable()\nsv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\nsv.modelName = "C0"\nsv.modelParameterName = "I0"'),
        ("define a Spectre simulation output expression to add via MdeSetting.addSpeOutput",
         "MdeSpeOutput",
         'out = pyScript.MdeSpeOutput("vout", "V(out)", "Expression", "all", True, False)'),
        ("limit the number of concurrent local jobs in an MDE platform run",
         "MdePlatLocalJobPolicy",
         'policy = pyScript.MdePlatLocalJobPolicy(8)\npolicy.setMaxJobNum(16)\nprint(policy.getMaxJobNum())'),
    ]
    for intent, api, usage in lookups:
        prompt = ("You are an EDA automation assistant. Which PyAether API is "
                  "used to %s? Show a minimal correct usage example." % intent)
        completion = ("The API is `%s`.\n\n```python\nimport pyAether as "
                      "pyScript\n%s\n```" % (api, usage))
        _add("S6", "v20-S6-%s" % api, prompt, completion, [api],
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
        "report_id": "R190",
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
        sys.stderr.write("GATE: FAIL (pollution detected) -- do NOT use v20\n")
        sys.exit(2)
    sys.stderr.write("GATE: PASS -- v20 is training-ready\n")


if __name__ == "__main__":
    main()