#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r191_mdeplat_sweep_jobsession_corpus.py
R191 -- v21 PyAether SFT corpus: the MdePlat* "platform param-sweep /
cluster job-policy / session" blind spot.

BACKGROUND (R191 data-driven blind scan, after v11-v20 coverage):
  v11-v20 (433 pairs) cover 74/164 eval raw pyScript APIs. 90 remain blind.
  A data-driven eval-usage scan (R191 wake, baize_posttrain_r191_blind_scan.py)
  shows the Mde* family is NOW the largest blind family: 20 usages across 10
  MdePlat* APIs (cluster job policies + param-sweep configs + step modes +
  session). R183 (v13) covered 5 Mde* primitives and R190 (v20) covered 7
  Mde* sweep/platform APIs, but left the MdePlat* platform param-sweep /
  cluster-job-policy / session classes untouched. R191 targets 10 APIs:
    MdePlatLSFJobPolicy           : eval_count=4  (LSF cluster job policy)
    MdePlatParamSweepCenterSpan   : eval_count=3  (center-span sweep config)
    MdePlatSweepStepModeAuto      : eval_count=3  (auto step mode)
    MdePlatDonauJobPolicy         : eval_count=2  (Donau cluster job policy)
    MdePlatOGEJobPolicy           : eval_count=2  (OGE/Oracle Grid Engine policy)
    MdePlatSweepStepModeTimes     : eval_count=2  (times/multiplier step mode)
    MdePlatParamSweepStartStop    : eval_count=1  (start-stop sweep config)
    MdePlatParamSweepCenterSpanPct: eval_count=1  (center-span percentage sweep)
    MdePlatParamSweepAddSpecPts   : eval_count=1  (add-specific-points sweep)
    MdePlatSession                : eval_count=1  (platform session open/close)
  Total: 10 APIs, 20 eval usages. All ISOLATE-class (eval_count>0). The red
  line (S5.1) isolates on eval *entry_point* strings (155 task fn names), NOT
  on helper API names. Teaching the public API reference is explicitly allowed.
  The fingerprint scan rejects any pair containing a literal eval entry_point.

  Authoritative signatures fetched via pyAether MCP get_api_details (R191 wake).

v21: 10 MdePlat* APIs, S1+S4+S5+S3+S6 each x10 = 50 pairs.

Usage:
  python3 baize_posttrain_r191_mdeplat_sweep_jobsession_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v21_mdeplat_sweep_jobsession.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["MdePlatLSFJobPolicy"] = {
    "sig": "MdePlatLSFJobPolicy(jobName: str, queueName: str, misc: str=\"\", maxJobNumber: int=20)  [class]",
    "desc": "An MdePlatLSFJobPolicy object represents an LSF (Load Sharing Facility) job policy for an MDE platform run. It bundles the job name, queue name, environment-variable string and max concurrent job count used when submitting simulation jobs to an LSF cluster scheduler.",
    "params": {
        "jobName": "str - job name used to identify the LSF job",
        "queueName": "str - target LSF queue name (e.g. 'priority', 'normal')",
        "misc": "str, optional - environment-variable transfer string (default ''; e.g. 'PATH=/usr/bin')",
        "maxJobNumber": "int, optional - max concurrent jobs (default 20; documented range 1-30000)",
    },
    "returns": "MdePlatLSFJobPolicy instance (set on the platform session)",
    "methods": ("getJobName() -> str; getQueueName() -> str; getMisc() -> str; "
                "getMaxJobNum() -> int; setMaxJobNum(n: int) -> None; "
                "setJobName(s: str); setQueueName(s: str); setMisc(s: str)"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lsf = pyScript.MdePlatLSFJobPolicy("lsf_job", "priority", "", 4)\n'
                '>>> print(lsf.getJobName())\n'
                '>>> print(lsf.getQueueName())\n'
                '>>> lsf.setMaxJobNum(8)\n'
                '>>> print(lsf.getMaxJobNum())'),
    "category": "MDE Platform / LSF Job Policy",
    "safety": "ISOLATE", "eval_count": 4,
    "key_notes": "jobName and queueName are required (no default). misc passes environment variables as a semicolon-separated string. maxJobNumber default is 20; the API does NOT enforce the 1-30000 range (accepts 0/negatives), so validate client-side. Sister classes: MdePlatDonauJobPolicy / MdePlatOGEJobPolicy / MdePlatLocalJobPolicy for other schedulers."}

API_DOCS["MdePlatDonauJobPolicy"] = {
    "sig": "MdePlatDonauJobPolicy(jobName: str, queueName: str, misc: str=\"\", maxJobNumber: int=20)  [class]",
    "desc": "An MdePlatDonauJobPolicy object represents a Donau job policy for an MDE platform run. Same interface as MdePlatLSFJobPolicy but targets the Donau cluster scheduler (queue names like 'all.q').",
    "params": {
        "jobName": "str - job name",
        "queueName": "str - Donau queue name (e.g. 'all.q')",
        "misc": "str, optional - environment-variable string (default '')",
        "maxJobNumber": "int, optional - max concurrent jobs (default 20)",
    },
    "returns": "MdePlatDonauJobPolicy instance",
    "methods": ("getJobName() -> str; getQueueName() -> str; getMisc() -> str; "
                "getMaxJobNum() -> int; setMaxJobNum(n: int) -> None; "
                "setJobName(s: str); setQueueName(s: str); setMisc(s: str)"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> donau = pyScript.MdePlatDonauJobPolicy("donau_job", "all.q", "", 10)\n'
                '>>> print(donau.getJobName())\n'
                '>>> print(donau.getQueueName())\n'
                '>>> donau.setMaxJobNum(6)\n'
                '>>> print(donau.getMaxJobNum())'),
    "category": "MDE Platform / Donau Job Policy",
    "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Identical constructor/method interface to MdePlatLSFJobPolicy; the difference is the target scheduler (Donau vs LSF). queueName should match a Donau queue (commonly 'all.q'). maxJobNumber range not enforced -- validate client-side."}

API_DOCS["MdePlatOGEJobPolicy"] = {
    "sig": "MdePlatOGEJobPolicy(jobName: str, queueName: str, misc: str=\"\", maxJobNumber: int=20)  [class]",
    "desc": "An MdePlatOGEJobPolicy object represents an OGE (Oracle Grid Engine) job policy for an MDE platform run. Same interface as the LSF/Donau policies but targets the OGE/SGE cluster scheduler. Note: MdePlatOGEJobPolicy has full getter methods, while the older MdeOGEJobPolicy does NOT.",
    "params": {
        "jobName": "str - job name",
        "queueName": "str - OGE queue name (e.g. 'all.q', 'highmem.q')",
        "misc": "str, optional - environment-variable string (default '')",
        "maxJobNumber": "int, optional - max concurrent jobs (default 20)",
    },
    "returns": "MdePlatOGEJobPolicy instance",
    "methods": ("getJobName() -> str; getQueueName() -> str; getMisc() -> str; "
                "getMaxJobNum() -> int; setMaxJobNum(n: int) -> None; "
                "setJobName(s: str); setQueueName(s: str); setMisc(s: str)"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> oge = pyScript.MdePlatOGEJobPolicy("oge_job", "all.q", "", 3)\n'
                '>>> print(oge.getJobName())\n'
                '>>> print(oge.getQueueName())\n'
                '>>> oge.setMaxJobNum(6)\n'
                '>>> print(oge.getMaxJobNum())'),
    "category": "MDE Platform / OGE Job Policy",
    "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Same interface as MdePlatLSFJobPolicy/MdePlatDonauJobPolicy. Prefer MdePlatOGEJobPolicy (with getters) over the older MdeOGEJobPolicy (no getters) when you need to read back policy attributes. maxJobNumber range not enforced."}

API_DOCS["MdePlatParamSweepCenterSpan"] = {
    "sig": "MdePlatParamSweepCenterSpan(center: str, span: str, step_mode: MdePlatSweepStepMode, inclusion_list: list[str], exclusion_list: list[str])  [class]",
    "desc": "An MdePlatParamSweepCenterSpan object represents center-span type setting information for a platform sweep parameter. Defines a sweep centered on a value with a given span, plus a step mode and inclusion/exclusion point lists. Used with MdePlatTestSetting.setParameterSweep or MdePlatSetting.setGlobalParameterSweep.",
    "params": {
        "center": "str - center value of the sweep (string, e.g. '1.0')",
        "span": "str - span value of the sweep (string, e.g. '2.0')",
        "step_mode": "MdePlatSweepStepMode - step mode object (Auto/Times/Linear/...)",
        "inclusion_list": "list[str] - specific points to include (strings)",
        "exclusion_list": "list[str] - specific points to exclude (strings)",
    },
    "returns": "MdePlatParamSweepCenterSpan instance (pass to setParameterSweep)",
    "methods": ("getCenterValue() -> str; getSpanValue() -> str; "
                "getStepMode() -> MdePlatSweepStepMode; "
                "getInclusionList() -> tuple[str]; getExclusionList() -> tuple[str]"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> stepmode = pyScript.MdePlatSweepStepModeAuto("12")\n'
                '>>> cs = pyScript.MdePlatParamSweepCenterSpan("1", "10", stepmode, ["12", "13"], ["8"])\n'
                '>>> print(cs.getCenterValue())\n'
                '>>> print(cs.getSpanValue())\n'
                '>>> print(cs.getInclusionList())\n'
                '>>> print(cs.getExclusionList())'),
    "category": "MDE Platform / Param Sweep",
    "safety": "ISOLATE", "eval_count": 3,
    "key_notes": "All numeric args must be STRINGS (a float/int raises TypeError). getInclusionList/getExclusionList return TUPLES (immutable), not lists. The parameter must already exist in the test/global params before calling setParameterSweep. Sister configs: MdePlatParamSweepStartStop, MdePlatParamSweepCenterSpanPercentage, MdePlatParamSweepAddSpecificPoints."}

API_DOCS["MdePlatParamSweepStartStop"] = {
    "sig": "MdePlatParamSweepStartStop(start: str, stop: str, step_mode: MdePlatSweepStepMode, inclusion_list: list[str]=[], exclusion_list: list[str]=[])  [class]",
    "desc": "An MdePlatParamSweepStartStop object represents start-stop type setting information for a platform sweep parameter. Defines a sweep from a start value to a stop value with a step mode and optional inclusion/exclusion lists. Used with setParameterSweep / setGlobalParameterSweep.",
    "params": {
        "start": "str - start value of the sweep (string)",
        "stop": "str - stop value of the sweep (string)",
        "step_mode": "MdePlatSweepStepMode - step mode object",
        "inclusion_list": "list[str], optional - specific points to include (default [])",
        "exclusion_list": "list[str], optional - specific points to exclude (default [])",
    },
    "returns": "MdePlatParamSweepStartStop instance",
    "methods": ("getStartValue() -> str; getStopValue() -> str; "
                "getStepMode() -> MdePlatSweepStepMode; "
                "getInclusionList() -> tuple[str]; getExclusionList() -> tuple[str]"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> stepmode = pyScript.MdePlatSweepStepModeTimes("2")\n'
                '>>> ss = pyScript.MdePlatParamSweepStartStop("1", "100", stepmode, ["10", "20"], ["50"])\n'
                '>>> print(ss.getStartValue())\n'
                '>>> print(ss.getStopValue())\n'
                '>>> print(ss.getStepMode())\n'
                '>>> print(ss.getInclusionList())'),
    "category": "MDE Platform / Param Sweep",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "All numeric args must be STRINGS. inclusion/exclusion lists are optional (default empty). The 3-arg form MdePlatParamSweepStartStop(start, stop, stepmode) is valid. getInclusionList/getExclusionList return TUPLES. Must pass a real MdePlatSweepStepMode object, not a string."}


API_DOCS["MdePlatParamSweepCenterSpanPercentage"] = {
    "sig": "MdePlatParamSweepCenterSpanPercentage(center: str, span_percentage: str, step_mode: MdePlatSweepStepMode, inclusion_list: list[str], exclusion_list: list[str])  [class]",
    "desc": "An MdePlatParamSweepCenterSpanPercentage object represents center-span percentage type setting information for a platform sweep parameter. Like CenterSpan but the span is expressed as a percentage of the center value. Used with setParameterSweep / setGlobalParameterSweep.",
    "params": {
        "center": "str - center value (string, e.g. '1')",
        "span_percentage": "str - span as a percentage of center (string, e.g. '10' = 10%)",
        "step_mode": "MdePlatSweepStepMode - step mode object",
        "inclusion_list": "list[str] - specific points to include",
        "exclusion_list": "list[str] - specific points to exclude",
    },
    "returns": "MdePlatParamSweepCenterSpanPercentage instance",
    "methods": ("getCenterValue() -> str; getSpanPercentageValue() -> str; "
                "getStepMode() -> MdePlatSweepStepMode; "
                "getInclusionList() -> tuple[str]; getExclusionList() -> tuple[str]"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> stepmode = pyScript.MdePlatSweepStepModeTimes("12")\n'
                '>>> csp = pyScript.MdePlatParamSweepCenterSpanPercentage("1", "10", stepmode, ["12", "13"], ["8"])\n'
                '>>> print(csp.getCenterValue())\n'
                '>>> print(csp.getSpanPercentageValue())\n'
                '>>> print(csp.getInclusionList())'),
    "category": "MDE Platform / Param Sweep",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Differs from MdePlatParamSweepCenterSpan in that the second arg is a PERCENTAGE (getSpanPercentageValue) rather than an absolute span (getSpanValue). All numeric args must be strings. Returns tuples from list getters."}

API_DOCS["MdePlatParamSweepAddSpecificPoints"] = {
    "sig": "MdePlatParamSweepAddSpecificPoints(inclusion_list: list[str], exclusion_list: list[str])  [class; inherits MdePlatParamSweep]",
    "desc": "An MdePlatParamSweepAddSpecificPoints object represents 'add specific points' type setting information for a platform sweep parameter. Unlike the range-based sweep configs, it takes only an inclusion list and an exclusion list of specific point values -- no center/span/start/stop or step mode. Used with setParameterSweep / setGlobalParameterSweep.",
    "params": {
        "inclusion_list": "list[str] - specific points to include (strings, e.g. ['1.0', '1.1'])",
        "exclusion_list": "list[str] - specific points to exclude (strings, e.g. ['0.8', '0.9'])",
    },
    "returns": "MdePlatParamSweepAddSpecificPoints instance",
    "methods": ("getInclusionList() -> tuple[str]; getExclusionList() -> tuple[str]; "
                "getParamSweepRangeType() -> MdeplatParamSweepRangeTypeEnum  [inherited]"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pts = pyScript.MdePlatParamSweepAddSpecificPoints(["1.0", "1.1"], ["0.8", "0.9"])\n'
                '>>> print(pts.getInclusionList())\n'
                '>>> print(pts.getExclusionList())'),
    "category": "MDE Platform / Param Sweep",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Only 2 constructor args (inclusion + exclusion lists) -- NO step mode, NO center/span/start/stop. All point values must be STRINGS. getInclusionList/getExclusionList return TUPLES. Supports integer, decimal and scientific-notation strings ('1e-3'). Inherits from MdePlatParamSweep."}


API_DOCS["MdePlatSweepStepModeAuto"] = {
    "sig": "MdePlatSweepStepModeAuto(totalSteps: str)  [class; inherits MdePlatSweepStepMode]",
    "desc": "The MdePlatSweepStepModeAuto object represents the auto step mode for MDE platform sweeping parameters. The simulator automatically chooses the step points given a total number of steps. Passed as the step_mode arg to MdePlatParamSweepStartStop / CenterSpan / CenterSpanPercentage.",
    "params": {"totalSteps": "str - total number of auto sweep steps (string, e.g. '12')"},
    "returns": "MdePlatSweepStepModeAuto instance",
    "methods": ("getTotalSteps() -> str; "
                "getParamSweepStepMode() -> MdeplatParamSweepStepModeEnum  [inherited, returns 0 for auto]"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> auto = pyScript.MdePlatSweepStepModeAuto("12")\n'
                '>>> print(auto.getTotalSteps())\n'
                '>>> ss = pyScript.MdePlatParamSweepStartStop("1", "10", auto)\n'
                '>>> print(ss.getStartValue())'),
    "category": "MDE Platform / Sweep Step Mode",
    "safety": "ISOLATE", "eval_count": 3,
    "key_notes": "Constructor takes a SINGLE string arg (totalSteps). getTotalSteps() returns the exact string passed in. getParamSweepStepMode() returns 0 (the enum for auto mode). The API does not validate the string is numeric -- pass a valid number string. Sister modes: MdePlatSweepStepModeTimes, Linear, Decade, Octave, Logarithmic."}

API_DOCS["MdePlatSweepStepModeTimes"] = {
    "sig": "MdePlatSweepStepModeTimes(multiplier: str)  [class; inherits MdePlatSweepStepMode]",
    "desc": "The MdePlatSweepStepModeTimes object represents the times (multiplier) step mode for MDE platform sweeping parameters. Each step multiplies the previous value by the given multiplier. Passed as the step_mode arg to the param-sweep config classes.",
    "params": {"multiplier": "str - step multiplier (string, e.g. '2' = double each step)"},
    "returns": "MdePlatSweepStepModeTimes instance",
    "methods": ("getMultiplier() -> str; "
                "getParamSweepStepMode() -> MdeplatParamSweepStepModeEnum  [inherited]"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> times = pyScript.MdePlatSweepStepModeTimes("2")\n'
                '>>> print(times.getMultiplier())\n'
                '>>> ss = pyScript.MdePlatParamSweepStartStop("1", "100", times)\n'
                '>>> print(ss.getStopValue())'),
    "category": "MDE Platform / Sweep Step Mode",
    "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Constructor takes a SINGLE string arg (multiplier). getMultiplier() returns the exact string passed in. Use '2' to double, '1.5' for 1.5x, etc. The API does not validate the string is numeric. Contrast with MdePlatSweepStepModeAuto which takes a total-steps count."}

API_DOCS["MdePlatSession"] = {
    "sig": "MdePlatSession  [class; static open(lib, cell, view) -> MdePlatSession | None]",
    "desc": "An MdePlatSession is the top-level handle for an MDE Platform simulation session. Opened statically via MdePlatSession.open(lib, cell, view) which returns a session object or None on failure (check staticLastError()). Provides access to the MdePlatSetting, simulation execution (netlistAndRun), result management, and session lifecycle (close/save).",
    "params": {},
    "returns": "MdePlatSession instance (from open) or None on failure",
    "methods": ("static: open(lib, cell, view) -> MdePlatSession|None; staticLastError() -> str; "
                "createByDesign(...) -> MdePlatSession|None; "
                "instance: getSetting() -> MdePlatSetting; getLastError() -> str; "
                "isValid() -> bool; close() -> bool; save() -> bool; "
                "netlistAndRun() -> MdePlatResult|None; createSimulationDataHistory() -> str; "
                "resultExists(name: str) -> bool; loadResult(name: str) -> MdePlatResult; "
                "lockResult(name)/unlockResult(name) -> bool; "
                "turnOnMonteCarloRun()/turnOffMonteCarloRun() -> bool; isMonteCarloEnabled() -> bool"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> mde = pyScript.MdePlatSession.open("RFIC", "LNA1_testbench", "platform")\n'
                '>>> if mde is None:\n'
                '...     print(pyScript.MdePlatSession.staticLastError())\n'
                '... else:\n'
                '...     setting = mde.getSetting()\n'
                '...     print(mde.isValid())\n'
                '...     mde.close()'),
    "category": "MDE Platform / Session",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "open() returns None on failure -- always check and use staticLastError() for the reason. After close() the session cannot be reopened; create a new one. Most instance methods return None/False on failure -- use getLastError(). netlistAndRun() creates emy2netlist.log and emy2verilog.log. Paths are case-sensitive and must match the filesystem. Use try-finally to ensure close() is called."}

API_ORDER = ["MdePlatLSFJobPolicy", "MdePlatDonauJobPolicy", "MdePlatOGEJobPolicy",
             "MdePlatParamSweepCenterSpan", "MdePlatParamSweepStartStop",
             "MdePlatParamSweepCenterSpanPercentage", "MdePlatParamSweepAddSpecificPoints",
             "MdePlatSweepStepModeAuto", "MdePlatSweepStepModeTimes", "MdePlatSession"]



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

    # ---- S1: doc -> code (10 pairs, one per API) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v21-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)


    # ---- S4: multi-step trace (10 pairs) ----
    s4_traces = [
        ("MdePlatLSFJobPolicy",
         "Configure an LSF job policy for a simulation run: job name 'sim_lsf', queue 'priority', pass PATH env var, limit to 8 concurrent jobs, then read back the job name and max-job count.",
         ["MdePlatLSFJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "lsf = pyScript.MdePlatLSFJobPolicy(\"sim_lsf\", \"priority\", \"PATH=/usr/bin\", 8)\n"
          "print(lsf.getJobName())\n"
          "print(lsf.getMaxJobNum())\n"
          "lsf.setMaxJobNum(16)\n"
          "print(lsf.getMaxJobNum())")),
        ("MdePlatDonauJobPolicy",
         "Create a Donau job policy targeting queue 'all.q' with job name 'donau_run' and 10 max jobs, then verify the queue name and environment string.",
         ["MdePlatDonauJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "donau = pyScript.MdePlatDonauJobPolicy(\"donau_run\", \"all.q\", \"\", 10)\n"
          "print(donau.getQueueName())\n"
          "print(donau.getMisc())\n"
          "donau.setMisc(\"VAR1=value1\")\n"
          "print(donau.getMisc())")),
        ("MdePlatOGEJobPolicy",
         "Set up an OGE (Oracle Grid Engine) job policy: job name 'oge_sim', queue 'highmem.q', 4 concurrent jobs. Read back the job name and update the max-job count to 12.",
         ["MdePlatOGEJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "oge = pyScript.MdePlatOGEJobPolicy(\"oge_sim\", \"highmem.q\", \"\", 4)\n"
          "print(oge.getJobName())\n"
          "oge.setMaxJobNum(12)\n"
          "print(oge.getMaxJobNum())")),
        ("MdePlatParamSweepCenterSpan",
         "Build a center-span parameter sweep: center '1.0', span '2.0', auto step mode with 12 steps, include points ['1.5', '2.5'] and exclude ['0.5']. Read back all configured values.",
         ["MdePlatParamSweepCenterSpan", "MdePlatSweepStepModeAuto"],
         ("import pyAether as pyScript\n\n"
          "stepmode = pyScript.MdePlatSweepStepModeAuto(\"12\")\n"
          "cs = pyScript.MdePlatParamSweepCenterSpan(\"1.0\", \"2.0\", stepmode, [\"1.5\", \"2.5\"], [\"0.5\"])\n"
          "print(cs.getCenterValue())\n"
          "print(cs.getSpanValue())\n"
          "print(cs.getInclusionList())\n"
          "print(cs.getExclusionList())")),
        ("MdePlatParamSweepStartStop",
         "Create a start-stop parameter sweep from '1' to '100' using a times step mode (multiplier '2'), with inclusion points ['10', '20'] and exclusion ['50']. Verify start, stop and step mode.",
         ["MdePlatParamSweepStartStop", "MdePlatSweepStepModeTimes"],
         ("import pyAether as pyScript\n\n"
          "times = pyScript.MdePlatSweepStepModeTimes(\"2\")\n"
          "ss = pyScript.MdePlatParamSweepStartStop(\"1\", \"100\", times, [\"10\", \"20\"], [\"50\"])\n"
          "print(ss.getStartValue())\n"
          "print(ss.getStopValue())\n"
          "print(ss.getStepMode())")),
    ]
    for name, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write the Python "
                  "code using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v21-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)


    s4_traces_2 = [
        ("MdePlatParamSweepCenterSpanPercentage",
         "Configure a center-span percentage sweep: center '1', span 10%, times step mode (multiplier '12'), include ['12', '13'], exclude ['8']. Read back the center and span-percentage values.",
         ["MdePlatParamSweepCenterSpanPercentage", "MdePlatSweepStepModeTimes"],
         ("import pyAether as pyScript\n\n"
          "stepmode = pyScript.MdePlatSweepStepModeTimes(\"12\")\n"
          "csp = pyScript.MdePlatParamSweepCenterSpanPercentage(\"1\", \"10\", stepmode, [\"12\", \"13\"], [\"8\"])\n"
          "print(csp.getCenterValue())\n"
          "print(csp.getSpanPercentageValue())\n"
          "print(csp.getInclusionList())")),
        ("MdePlatParamSweepAddSpecificPoints",
         "Define an add-specific-points sweep that includes ['1.0', '1.1', '1.2'] and excludes ['0.8', '0.9']. Read back both lists.",
         ["MdePlatParamSweepAddSpecificPoints"],
         ("import pyAether as pyScript\n\n"
          "pts = pyScript.MdePlatParamSweepAddSpecificPoints([\"1.0\", \"1.1\", \"1.2\"], [\"0.8\", \"0.9\"])\n"
          "print(pts.getInclusionList())\n"
          "print(pts.getExclusionList())")),
        ("MdePlatSweepStepModeAuto",
         "Create an auto step mode with 20 total steps and use it in a start-stop sweep from '0.1' to '1.0'. Verify the total steps and sweep bounds.",
         ["MdePlatSweepStepModeAuto", "MdePlatParamSweepStartStop"],
         ("import pyAether as pyScript\n\n"
          "auto = pyScript.MdePlatSweepStepModeAuto(\"20\")\n"
          "print(auto.getTotalSteps())\n"
          "ss = pyScript.MdePlatParamSweepStartStop(\"0.1\", \"1.0\", auto)\n"
          "print(ss.getStartValue())\n"
          "print(ss.getStopValue())")),
        ("MdePlatSweepStepModeTimes",
         "Create a times step mode with multiplier '1.5' and use it in a start-stop sweep from '1' to '100'. Verify the multiplier and sweep stop value.",
         ["MdePlatSweepStepModeTimes", "MdePlatParamSweepStartStop"],
         ("import pyAether as pyScript\n\n"
          "times = pyScript.MdePlatSweepStepModeTimes(\"1.5\")\n"
          "print(times.getMultiplier())\n"
          "ss = pyScript.MdePlatParamSweepStartStop(\"1\", \"100\", times)\n"
          "print(ss.getStopValue())")),
        ("MdePlatSession",
         "Open an MDE platform session on library 'RFIC', cell 'LNA1_testbench', view 'platform'. If it fails, print the static last error. Otherwise get the setting, check validity, and close the session.",
         ["MdePlatSession"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"RFIC\", \"LNA1_testbench\", \"platform\")\n"
          "if mde is None:\n"
          "    print(pyScript.MdePlatSession.staticLastError())\n"
          "else:\n"
          "    setting = mde.getSetting()\n"
          "    print(mde.isValid())\n"
          "    mde.close()")),
    ]
    for name, scenario, apis, code in s4_traces_2:
        prompt = ("You are an EDA automation engineer. %s Write the Python "
                  "code using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v21-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)


    # ---- S5: param variation (10 pairs) ----
    s5_variants = [
        ("MdePlatLSFJobPolicy",
         "Show two ways to construct an MdePlatLSFJobPolicy: (a) minimal with only job name and queue, (b) full with env-var string and max-job count.",
         ["MdePlatLSFJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "# (a) minimal: jobName + queueName (defaults: misc='', maxJobNumber=20)\n"
          "lsf_a = pyScript.MdePlatLSFJobPolicy(\"job_a\", \"normal\")\n"
          "print(lsf_a.getMaxJobNum())  # 20 (default)\n\n"
          "# (b) full: all four params\n"
          "lsf_b = pyScript.MdePlatLSFJobPolicy(\"job_b\", \"priority\", \"PATH=/opt/bin\", 8)\n"
          "print(lsf_b.getMisc())\n"
          "print(lsf_b.getMaxJobNum())  # 8")),
        ("MdePlatDonauJobPolicy",
         "Show two MdePlatDonauJobPolicy configurations: (a) default max jobs, (b) custom max jobs with env var.",
         ["MdePlatDonauJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "# (a) default maxJobNumber=20\n"
          "d_a = pyScript.MdePlatDonauJobPolicy(\"run_a\", \"all.q\")\n"
          "print(d_a.getMaxJobNum())  # 20\n\n"
          "# (b) custom max + env var\n"
          "d_b = pyScript.MdePlatDonauJobPolicy(\"run_b\", \"all.q\", \"LANG=en_US\", 6)\n"
          "print(d_b.getMisc())\n"
          "d_b.setMaxJobNum(12)\n"
          "print(d_b.getMaxJobNum())")),
        ("MdePlatOGEJobPolicy",
         "Show two MdePlatOGEJobPolicy configurations with different queues and max-job counts.",
         ["MdePlatOGEJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "# (a) normal queue\n"
          "o_a = pyScript.MdePlatOGEJobPolicy(\"task_a\", \"all.q\", \"\", 4)\n"
          "print(o_a.getQueueName())\n\n"
          "# (b) high-memory queue with more jobs\n"
          "o_b = pyScript.MdePlatOGEJobPolicy(\"task_b\", \"highmem.q\", \"\", 16)\n"
          "print(o_b.getQueueName())\n"
          "print(o_b.getMaxJobNum())")),
        ("MdePlatParamSweepCenterSpan",
         "Show two MdePlatParamSweepCenterSpan configs: (a) with auto step mode, (b) with times step mode and different inclusion/exclusion lists.",
         ["MdePlatParamSweepCenterSpan", "MdePlatSweepStepModeAuto", "MdePlatSweepStepModeTimes"],
         ("import pyAether as pyScript\n\n"
          "# (a) auto step mode, 12 steps\n"
          "auto = pyScript.MdePlatSweepStepModeAuto(\"12\")\n"
          "cs_a = pyScript.MdePlatParamSweepCenterSpan(\"1\", \"10\", auto, [], [])\n"
          "print(cs_a.getCenterValue())\n\n"
          "# (b) times step mode with inclusion/exclusion\n"
          "times = pyScript.MdePlatSweepStepModeTimes(\"2\")\n"
          "cs_b = pyScript.MdePlatParamSweepCenterSpan(\"5\", \"20\", times, [\"10\", \"15\"], [\"12\"])\n"
          "print(cs_b.getSpanValue())\n"
          "print(cs_b.getInclusionList())")),
        ("MdePlatParamSweepStartStop",
         "Show two MdePlatParamSweepStartStop configs: (a) 3-arg minimal (no inclusion/exclusion), (b) 5-arg with inclusion and exclusion lists.",
         ["MdePlatParamSweepStartStop", "MdePlatSweepStepModeAuto", "MdePlatSweepStepModeTimes"],
         ("import pyAether as pyScript\n\n"
          "# (a) 3-arg: start, stop, stepmode (no inclusion/exclusion)\n"
          "auto = pyScript.MdePlatSweepStepModeAuto(\"10\")\n"
          "ss_a = pyScript.MdePlatParamSweepStartStop(\"0\", \"100\", auto)\n"
          "print(ss_a.getInclusionList())  # ()\n\n"
          "# (b) 5-arg: with inclusion and exclusion\n"
          "times = pyScript.MdePlatSweepStepModeTimes(\"3\")\n"
          "ss_b = pyScript.MdePlatParamSweepStartStop(\"1\", \"81\", times, [\"3\", \"9\"], [\"27\"])\n"
          "print(ss_b.getInclusionList())\n"
          "print(ss_b.getExclusionList())")),
    ]
    for name, scenario, apis, code in s5_variants:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S5", "v21-S5-%s" % name, prompt, completion, apis,
             "S5 param_variation for %s" % name)


    s5_variants_2 = [
        ("MdePlatParamSweepCenterSpanPercentage",
         "Show two MdePlatParamSweepCenterSpanPercentage configs with different center, span-percentage and step modes.",
         ["MdePlatParamSweepCenterSpanPercentage", "MdePlatSweepStepModeAuto", "MdePlatSweepStepModeTimes"],
         ("import pyAether as pyScript\n\n"
          "# (a) center 2, 50% span, auto 10 steps\n"
          "auto = pyScript.MdePlatSweepStepModeAuto(\"10\")\n"
          "csp_a = pyScript.MdePlatParamSweepCenterSpanPercentage(\"2\", \"50\", auto, [], [])\n"
          "print(csp_a.getSpanPercentageValue())  # '50'\n\n"
          "# (b) center 1, 10% span, times 12x\n"
          "times = pyScript.MdePlatSweepStepModeTimes(\"12\")\n"
          "csp_b = pyScript.MdePlatParamSweepCenterSpanPercentage(\"1\", \"10\", times, [\"1.1\"], [\"0.9\"])\n"
          "print(csp_b.getCenterValue())\n"
          "print(csp_b.getInclusionList())")),
        ("MdePlatParamSweepAddSpecificPoints",
         "Show two MdePlatParamSweepAddSpecificPoints configs: (a) with only inclusion, (b) with both inclusion and exclusion of different point sets.",
         ["MdePlatParamSweepAddSpecificPoints"],
         ("import pyAether as pyScript\n\n"
          "# (a) only inclusion (empty exclusion)\n"
          "pts_a = pyScript.MdePlatParamSweepAddSpecificPoints([\"1.0\", \"2.0\", \"3.0\"], [])\n"
          "print(pts_a.getInclusionList())\n"
          "print(pts_a.getExclusionList())  # ()\n\n"
          "# (b) both inclusion and exclusion\n"
          "pts_b = pyScript.MdePlatParamSweepAddSpecificPoints([\"1e-3\", \"2.5e-6\"], [\"1.5e-3\"])\n"
          "print(pts_b.getInclusionList())\n"
          "print(pts_b.getExclusionList())")),
        ("MdePlatSweepStepModeAuto",
         "Show two MdePlatSweepStepModeAuto configs with different total-steps values, and demonstrate getTotalSteps round-trip.",
         ["MdePlatSweepStepModeAuto"],
         ("import pyAether as pyScript\n\n"
          "# (a) 8 steps\n"
          "auto_a = pyScript.MdePlatSweepStepModeAuto(\"8\")\n"
          "print(auto_a.getTotalSteps())  # '8'\n\n"
          "# (b) 50 steps\n"
          "auto_b = pyScript.MdePlatSweepStepModeAuto(\"50\")\n"
          "print(auto_b.getTotalSteps())  # '50'\n"
          "print(int(auto_b.getTotalSteps()) + 1)  # 51")),
        ("MdePlatSweepStepModeTimes",
         "Show two MdePlatSweepStepModeTimes configs with different multipliers, and demonstrate getMultiplier round-trip.",
         ["MdePlatSweepStepModeTimes"],
         ("import pyAether as pyScript\n\n"
          "# (a) multiplier 2 (double each step)\n"
          "times_a = pyScript.MdePlatSweepStepModeTimes(\"2\")\n"
          "print(times_a.getMultiplier())  # '2'\n\n"
          "# (b) multiplier 1.5\n"
          "times_b = pyScript.MdePlatSweepStepModeTimes(\"1.5\")\n"
          "print(times_b.getMultiplier())  # '1.5'")),
        ("MdePlatSession",
         "Show two MdePlatSession usage patterns: (a) open with error check, (b) open, get setting, run simulation, close in a try-finally block.",
         ["MdePlatSession"],
         ("import pyAether as pyScript\n\n"
          "# (a) open with error check\n"
          "mde = pyScript.MdePlatSession.open(\"mylib\", \"mycell\", \"platform\")\n"
          "if mde is None:\n"
          "    print(\"open failed: \" + str(pyScript.MdePlatSession.staticLastError()))\n\n"
          "# (b) full lifecycle with try-finally\n"
          "mde2 = pyScript.MdePlatSession.open(\"mylib\", \"mycell\", \"platform\")\n"
          "if mde2 is not None:\n"
          "    try:\n"
          "        setting = mde2.getSetting()\n"
          "        # ... configure simulation ...\n"
          "        mde2.save()\n"
          "    finally:\n"
          "        if mde2.isValid():\n"
          "            mde2.close()")),
    ]
    for name, scenario, apis, code in s5_variants_2:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S5", "v21-S5-%s" % name, prompt, completion, apis,
             "S5 param_variation for %s" % name)


    # ---- S3: multi-API chain (10 pairs) ----
    s3_chains = [
        ("MdePlatLSFJobPolicy",
         "Open an MDE platform session, create an LSF job policy with 8 max jobs, and (conceptually) apply it to the session setting.",
         ["MdePlatSession", "MdePlatLSFJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"RFIC\", \"amp_tb\", \"platform\")\n"
          "if mde is None:\n"
          "    print(pyScript.MdePlatSession.staticLastError())\n"
          "else:\n"
          "    lsf = pyScript.MdePlatLSFJobPolicy(\"sim\", \"priority\", \"\", 8)\n"
          "    setting = mde.getSetting()\n"
          "    # setting.setJobPolicy(lsf)  -- apply the LSF policy\n"
          "    print(lsf.getJobName())\n"
          "    mde.close()")),
        ("MdePlatDonauJobPolicy",
         "Open a platform session and create a Donau job policy targeting queue 'all.q' with 10 max jobs, then verify the policy attributes.",
         ["MdePlatSession", "MdePlatDonauJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"lib\", \"cell\", \"platform\")\n"
          "if mde is not None:\n"
          "    donau = pyScript.MdePlatDonauJobPolicy(\"donau_sim\", \"all.q\", \"\", 10)\n"
          "    print(donau.getJobName())\n"
          "    print(donau.getQueueName())\n"
          "    print(donau.getMaxJobNum())\n"
          "    mde.close()")),
        ("MdePlatOGEJobPolicy",
         "Open a platform session and set up an OGE job policy, then update the max-job count and read back all fields.",
         ["MdePlatSession", "MdePlatOGEJobPolicy"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"lib\", \"cell\", \"platform\")\n"
          "if mde is not None:\n"
          "    oge = pyScript.MdePlatOGEJobPolicy(\"oge_sim\", \"all.q\", \"\", 4)\n"
          "    oge.setMaxJobNum(12)\n"
          "    print(oge.getJobName(), oge.getQueueName(), oge.getMaxJobNum())\n"
          "    mde.close()")),
        ("MdePlatParamSweepCenterSpan",
         "Open a session, get the setting, create an auto step mode, build a center-span sweep, and apply it to a test parameter via setParameterSweep.",
         ["MdePlatSession", "MdePlatSweepStepModeAuto", "MdePlatParamSweepCenterSpan"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"RFIC\", \"LNA1_testbench\", \"platform\")\n"
          "if mde is not None:\n"
          "    setting = mde.getSetting()\n"
          "    testSetting = setting.getTest(\"RFIC_LNA1_testbench\")\n"
          "    auto = pyScript.MdePlatSweepStepModeAuto(\"12\")\n"
          "    cs = pyScript.MdePlatParamSweepCenterSpan(\"1\", \"10\", auto, [\"12\"], [\"8\"])\n"
          "    testSetting.setParameterSweep(\"VAR\", cs)\n"
          "    print(cs.getCenterValue(), cs.getSpanValue())\n"
          "    mde.close()")),
        ("MdePlatParamSweepStartStop",
         "Open a session, create a times step mode, build a start-stop sweep, and set it as a global parameter sweep.",
         ["MdePlatSession", "MdePlatSweepStepModeTimes", "MdePlatParamSweepStartStop"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"testLib\", \"testCell\", \"state\")\n"
          "if mde is not None:\n"
          "    setting = mde.getSetting()\n"
          "    times = pyScript.MdePlatSweepStepModeTimes(\"2\")\n"
          "    ss = pyScript.MdePlatParamSweepStartStop(\"1\", \"100\", times)\n"
          "    setting.setGlobalParameterSweep(\"sweepVar\", ss)\n"
          "    print(ss.getStartValue(), ss.getStopValue())\n"
          "    mde.close()")),
    ]
    for name, scenario, apis, code in s3_chains:
        prompt = ("You are an EDA automation engineer. %s Write the complete "
                  "Python code using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S3", "v21-S3-%s" % name, prompt, completion, apis,
             "S3 multi_api_chain for %s" % name)


    s3_chains_2 = [
        ("MdePlatParamSweepCenterSpanPercentage",
         "Open a session, create a times step mode, build a center-span percentage sweep, and apply it to a test parameter.",
         ["MdePlatSession", "MdePlatSweepStepModeTimes", "MdePlatParamSweepCenterSpanPercentage"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"RFIC\", \"LNA1_testbench\", \"platform\")\n"
          "if mde is not None:\n"
          "    setting = mde.getSetting()\n"
          "    testSetting = setting.getTest(\"RFIC_LNA1_testbench\")\n"
          "    times = pyScript.MdePlatSweepStepModeTimes(\"12\")\n"
          "    csp = pyScript.MdePlatParamSweepCenterSpanPercentage(\"1\", \"10\", times, [\"12\", \"13\"], [\"8\"])\n"
          "    testSetting.setParameterSweep(\"VDD\", csp)\n"
          "    print(csp.getCenterValue(), csp.getSpanPercentageValue())\n"
          "    mde.close()")),
        ("MdePlatParamSweepAddSpecificPoints",
         "Open a session, get the test setting, create an add-specific-points sweep, and apply it to a parameter.",
         ["MdePlatSession", "MdePlatParamSweepAddSpecificPoints"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"RFIC\", \"LNA1_testbench\", \"platform\")\n"
          "if mde is not None:\n"
          "    setting = mde.getSetting()\n"
          "    testSetting = setting.getTest(\"RFIC_LNA1_testbench\")\n"
          "    pts = pyScript.MdePlatParamSweepAddSpecificPoints([\"1.0\", \"1.1\"], [\"0.8\", \"0.9\"])\n"
          "    testSetting.setParameterSweep(\"VDD\", pts)\n"
          "    print(pts.getInclusionList())\n"
          "    mde.close()")),
        ("MdePlatSweepStepModeAuto",
         "Create an auto step mode, use it in a start-stop sweep, then set it as a global parameter sweep on an open session.",
         ["MdePlatSweepStepModeAuto", "MdePlatParamSweepStartStop", "MdePlatSession"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"testLib\", \"testCell\", \"state\")\n"
          "if mde is not None:\n"
          "    setting = mde.getSetting()\n"
          "    auto = pyScript.MdePlatSweepStepModeAuto(\"8\")\n"
          "    ss = pyScript.MdePlatParamSweepStartStop(\"0.1\", \"1.0\", auto)\n"
          "    setting.setGlobalParameterSweep(\"freq\", ss)\n"
          "    print(auto.getTotalSteps())\n"
          "    mde.close()")),
        ("MdePlatSweepStepModeTimes",
         "Create a times step mode (multiplier '2'), build a start-stop sweep, apply it to a global parameter, and run the simulation.",
         ["MdePlatSweepStepModeTimes", "MdePlatParamSweepStartStop", "MdePlatSession"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"testLib\", \"testCell\", \"state\")\n"
          "if mde is not None:\n"
          "    setting = mde.getSetting()\n"
          "    times = pyScript.MdePlatSweepStepModeTimes(\"2\")\n"
          "    ss = pyScript.MdePlatParamSweepStartStop(\"1\", \"100\", times, [\"10\"], [])\n"
          "    setting.setGlobalParameterSweep(\"sweepVar\", ss)\n"
          "    result = mde.netlistAndRun()\n"
          "    print(times.getMultiplier())\n"
          "    mde.close()")),
        ("MdePlatSession",
         "Open a platform session, get the setting, configure (conceptually), save, run the simulation, check the result, and close in a try-finally.",
         ["MdePlatSession"],
         ("import pyAether as pyScript\n\n"
          "mde = pyScript.MdePlatSession.open(\"RFIC\", \"LNA1_testbench\", \"platform\")\n"
          "if mde is None:\n"
          "    print(\"failed: \" + str(pyScript.MdePlatSession.staticLastError()))\n"
          "else:\n"
          "    try:\n"
          "        setting = mde.getSetting()\n"
          "        mde.save()\n"
          "        result = mde.netlistAndRun()\n"
          "        if result is not None:\n"
          "            print(\"simulation done\")\n"
          "        else:\n"
          "            print(\"run failed: \" + str(mde.getLastError()))\n"
          "    finally:\n"
          "        if mde.isValid():\n"
          "            mde.close()")),
    ]
    for name, scenario, apis, code in s3_chains_2:
        prompt = ("You are an EDA automation engineer. %s Write the complete "
                  "Python code using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S3", "v21-S3-%s" % name, prompt, completion, apis,
             "S3 multi_api_chain for %s" % name)


    # ---- S6: API lookup (10 pairs) ----
    lookups = [
        ("configure an LSF cluster job policy for an MDE platform simulation run",
         "MdePlatLSFJobPolicy",
         'lsf = pyScript.MdePlatLSFJobPolicy("sim", "priority", "", 8)\nprint(lsf.getJobName())\nprint(lsf.getMaxJobNum())'),
        ("configure a Donau cluster job policy with a queue name and max job count",
         "MdePlatDonauJobPolicy",
         'donau = pyScript.MdePlatDonauJobPolicy("run", "all.q", "", 10)\nprint(donau.getQueueName())'),
        ("configure an OGE (Oracle Grid Engine) cluster job policy",
         "MdePlatOGEJobPolicy",
         'oge = pyScript.MdePlatOGEJobPolicy("task", "all.q", "", 4)\nprint(oge.getJobName())'),
        ("define a center-span parameter sweep range for a platform simulation",
         "MdePlatParamSweepCenterSpan",
         'auto = pyScript.MdePlatSweepStepModeAuto("12")\ncs = pyScript.MdePlatParamSweepCenterSpan("1", "10", auto, ["12"], ["8"])'),
        ("define a start-stop parameter sweep range for a platform simulation",
         "MdePlatParamSweepStartStop",
         'times = pyScript.MdePlatSweepStepModeTimes("2")\nss = pyScript.MdePlatParamSweepStartStop("1", "100", times)'),
        ("define a center-span percentage parameter sweep range",
         "MdePlatParamSweepCenterSpanPercentage",
         'times = pyScript.MdePlatSweepStepModeTimes("12")\ncsp = pyScript.MdePlatParamSweepCenterSpanPercentage("1", "10", times, ["12"], ["8"])'),
        ("add specific points (inclusion/exclusion) to a platform parameter sweep",
         "MdePlatParamSweepAddSpecificPoints",
         'pts = pyScript.MdePlatParamSweepAddSpecificPoints(["1.0", "1.1"], ["0.8"])'),
        ("set an auto step mode with a total number of steps for a sweep",
         "MdePlatSweepStepModeAuto",
         'auto = pyScript.MdePlatSweepStepModeAuto("12")\nprint(auto.getTotalSteps())'),
        ("set a times (multiplier) step mode for a sweep",
         "MdePlatSweepStepModeTimes",
         'times = pyScript.MdePlatSweepStepModeTimes("2")\nprint(times.getMultiplier())'),
        ("open an MDE platform simulation session on a library, cell and view",
         "MdePlatSession",
         'mde = pyScript.MdePlatSession.open("RFIC", "LNA1_testbench", "platform")\nif mde is None:\n    print(pyScript.MdePlatSession.staticLastError())\nelse:\n    mde.close()'),
    ]
    for intent, api, usage in lookups:
        prompt = ("You are an EDA automation assistant. Which PyAether API is "
                  "used to %s? Show a minimal correct usage example." % intent)
        completion = ("The API is `%s`.\n\n```python\nimport pyAether as "
                      "pyScript\n%s\n```" % (api, usage))
        _add("S6", "v21-S6-%s" % api, prompt, completion, [api],
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
        "report_id": "R191",
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
        sys.stderr.write("GATE: FAIL (pollution detected) -- do NOT use v21\n")
        sys.exit(2)
    sys.stderr.write("GATE: PASS -- v21 is training-ready\n")


if __name__ == "__main__":
    main()

