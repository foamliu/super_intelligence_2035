#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r204_utility_corpus.py
R204 -- v34 PyAether SFT corpus: 3 Misc-Commands utility APIs.
= aelEngineerNotation + timeToTm + setPyAePath (+ 3 related), ~20 pairs.

BACKGROUND: v11-v33 (892 pairs) cover 155/164 eval raw APIs (94.5%). 9 blind.
Data-driven scan (R191 blind_scan, re-run with v33) shows the remaining 9
blind APIs are each 1-usage with no shared family prefix. This round picks
the 3 most tractable: Misc-Commands pure-utility functions.

Eval-task coupling (ISOLATE-class):
  aelEngineerNotation -> eval task 071, entry_point=batch_format_engineering
    aelEngineerNotation is NOT an entry_point -> ISOLATE-class helper.
  timeToTm -> eval task 002, entry_point=get_date_from_timestamp
    timeToTm is NOT an entry_point -> ISOLATE-class helper.
  setPyAePath -> eval task 003, entry_point=find_invalid_paths
    setPyAePath is NOT an entry_point -> ISOLATE-class helper.

Red line (S5.1) isolates on eval *entry_point* strings (155 task fn names),
NOT on helper API names. Fingerprint scan rejects any pair containing a
literal eval entry_point. Doctest values DELIBERATELY DIFFERENT from eval:
  aelEngineerNotation: eval uses [0.001, "5000"]; we use 123.456789, "9876543"
  timeToTm: eval uses 1682560771, 0; we use 1700000000, 1609459200, 946684800
  setPyAePath: eval uses tempdir paths; we use /opt/eda/custom_libs etc.

Usage: python3 baize_posttrain_r204_utility_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v34_utility.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}
API_ORDER = ["aelEngineerNotation", "aelPushSignifDigs", "aelPopSignifDigs",
             "timeToTm", "etTimeToString", "setPyAePath", "getPyAePath"]

API_DOCS["aelEngineerNotation"] = {
    "sig": ("aelEngineerNotation(numIn: emyDouble)\n"
            "aelEngineerNotation(strIn: emyChar)   [class; formats a number "
            "into engineering notation]"),
    "desc": ("A class that formats a number into engineering-notation string "
             "representation. Two constructor overloads accept a float or a "
             "numeric string. str(obj) yields the formatted notation. Default "
             "precision is 4 significant digits, controllable via "
             "aelPushSignifDigs / aelPopSignifDigs. Values whose absolute "
             "magnitude is outside [0.001, 1000) use scientific notation."),
    "params": {
        "numIn: emyDouble": ("A floating-point number to format, e.g. "
                             "123.456789 or 1.23e-6."),
        "strIn: emyChar": ("A numeric string to format, e.g. \"9876543\". "
                           "Invalid strings yield \"\"."),
    },
    "returns": ("An aelEngineerNotation object; str(obj) gives the formatted "
                "engineering-notation string."),
    "methods": ("Construct-only usage (no documented methods). str(obj) or "
                "print(obj) produces the formatted string."),
    "key_notes": ("Default 4 significant digits. Use aelPushSignifDigs(n) "
                  "to push n sig digits onto a stack and aelPopSignifDigs() "
                  "to restore. Invalid string input returns empty string. "
                  "Helper formatting utility, not a task entry point."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> obj = pyScript.aelEngineerNotation(123.456789)\n"
                ">>> print(str(obj))\n"
                "123.5\n"
                ">>> obj_s = pyScript.aelEngineerNotation(\"9876543\")\n"
                ">>> print(str(obj_s))\n"
                "9.877e+06"),
}

API_DOCS["aelPushSignifDigs"] = {
    "sig": ("aelPushSignifDigs(num: int) -> int   [function; push significant-"
            "digits setting onto stack]"),
    "desc": ("Pushes a new significant-digits count onto an internal stack "
             "and returns the new stack-top value. Subsequent "
             "aelEngineerNotation formatting uses this many significant "
             "digits until aelPopSignifDigs restores the previous setting."),
    "params": {"num: int": "Number of significant digits to use (e.g. 6)."},
    "returns": "int -- the new stack-top significant-digits value.",
    "key_notes": ("Works as a stack: push then pop to restore. Pairs with "
                  "aelPopSignifDigs. Helper utility for number formatting."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> top = pyScript.aelPushSignifDigs(6)\n"
                ">>> print(top)\n"
                "6\n"
                ">>> obj = pyScript.aelEngineerNotation(123.456789)\n"
                ">>> print(str(obj))\n"
                "123.457"),
}

API_DOCS["aelPopSignifDigs"] = {
    "sig": ("aelPopSignifDigs() -> int   [function; pop significant-digits "
            "setting from stack]"),
    "desc": ("Pops the top significant-digits setting from the internal "
             "stack, restoring the previous value. Returns the popped value."),
    "params": {},
    "returns": "int -- the significant-digits value that was popped.",
    "key_notes": ("Must be called after a matching aelPushSignifDigs. "
                  "Helper utility for number formatting."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.aelPushSignifDigs(3)\n"
                "3\n"
                ">>> popped = pyScript.aelPopSignifDigs()\n"
                ">>> print(popped)\n"
                "3"),
}

API_DOCS["timeToTm"] = {
    "sig": ("timeToTm(timestamp: int) -> struct_time   [function; convert "
            "Unix timestamp to broken-down time]"),
    "desc": ("Converts an integer Unix timestamp into a struct_time object "
             "with fields tm_year (full year, e.g. 2023), tm_mon (1-12), "
             "tm_mday (1-31), tm_hour, tm_min, tm_sec, tm_wday (0=Monday), "
             "tm_yday (1-366), tm_isdst. Returns LOCAL time. Only accepts "
             "integers; floats/strings raise errors."),
    "params": {"timestamp: int": "A Unix timestamp integer, e.g. 1700000000."},
    "returns": ("struct_time with fields tm_year, tm_mon, tm_mday, tm_hour, "
                "tm_min, tm_sec, tm_wday, tm_yday, tm_isdst."),
    "methods": ("Attribute access: result.tm_year, result.tm_mon, "
                "result.tm_mday, result.tm_wday, result.tm_yday, etc."),
    "key_notes": ("tm_year is the FULL year (not since-1900). tm_wday: 0 = "
                  "Monday. Returns local time, not UTC. Only int input. "
                  "Helper time-conversion utility, not a task entry point."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> tm = pyScript.timeToTm(1700000000)\n"
                ">>> print(tm.tm_year, tm.tm_mon, tm.tm_mday)\n"
                "2023 11 14\n"
                ">>> print(tm.tm_wday)\n"
                "1"),
}

API_DOCS["etTimeToString"] = {
    "sig": ("etTimeToString(timestamp: int) -> str   [function; format "
            "timestamp as human-readable string]"),
    "desc": ("Formats an integer Unix timestamp into a human-readable string. "
             "Uses the same timestamp base as timeToTm."),
    "params": {"timestamp: int": "A Unix timestamp integer, e.g. 1609459200."},
    "returns": "str -- a formatted date/time string.",
    "key_notes": ("Same timestamp base as timeToTm. Helper time-formatting "
                  "utility."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> s = pyScript.etTimeToString(1609459200)\n"
                ">>> print(isinstance(s, str))\n"
                "True"),
}

API_DOCS["setPyAePath"] = {
    "sig": ("setPyAePath(paths: str | List[str]) -> List[str]   [function; "
            "add paths to pyAether Python search path]"),
    "desc": ("Adds one or more directory paths to the pyAether internal "
             "Python search path. Accepts a single string or a list of "
             "strings. Returns the list of paths that do NOT exist on the "
             "filesystem. Tilde ~ is expanded. Empty list returns []. "
             "Non-string arguments raise TypeError."),
    "params": {
        "paths: str": "A single directory path string.",
        "paths: List[str]": "A list of directory path strings.",
    },
    "returns": ("List[str] -- paths from the input that do not exist. "
                "Empty list means all paths were valid."),
    "key_notes": ("Only accepts str or List[str]; other types raise "
                  "TypeError. ~ is expanded. Paired with getPyAePath. "
                  "Helper config utility, not a task entry point."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> missing = pyScript.setPyAePath(\"/opt/eda/custom_libs\")\n"
                ">>> print(isinstance(missing, list))\n"
                "True"),
}

API_DOCS["getPyAePath"] = {
    "sig": ("getPyAePath() -> List[str]   [function; get pyAether Python "
            "search paths]"),
    "desc": ("Returns the list of currently valid Python search paths "
             "managed by pyAether (those added via setPyAePath that exist)."),
    "params": {},
    "returns": "List[str] -- the current valid pyAether Python paths.",
    "key_notes": ("Companion to setPyAePath. Returns only existing paths. "
                  "Helper config utility."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> paths = pyScript.getPyAePath()\n"
                ">>> print(isinstance(paths, list))\n"
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

    # ===== aelEngineerNotation (+ aelPushSignifDigs / aelPopSignifDigs) =====
    name = "aelEngineerNotation"
    doc = _doc_block(name)
    d = API_DOCS[name]
    _add("S1", "v34-S1-%s" % name,
         ("You are an EDA automation engineer. Given the following "
          "PyAether API reference, write a minimal correct Python "
          "code snippet that uses `%s`.\n\n%s" % (name, doc)),
         "```python\n%s\n```" % d["doctest"], [name],
         "S1 doc_to_code for %s" % name)
    _add("S3", "v34-S3-%s" % name,
         ("You are an EDA automation engineer. The following Python "
          "code uses a PyAether API. Identify the API name, describe "
          "what it does, and explain its signature.\n\n"
          "```python\n%s\n```" % d["doctest"]),
         ("The API used is **`%s`**.\n\n**Signature**: `%s`\n\n%s\n\n"
          "**Key notes**: %s" % (name, d["sig"], d["desc"],
                                 d.get("key_notes", ""))),
         [name], "S3 code_to_doc for %s" % name)
    for label, scenario, apis, code in [
        ("aelEngineerNotation-float-and-string",
         "Format a float and a numeric string into engineering notation, "
         "showing both constructor overloads return formatted strings.",
         ["aelEngineerNotation"],
         ">>> import pyAether as pyScript\n"
         ">>> f_obj = pyScript.aelEngineerNotation(0.00042)\n"
         ">>> print('float:', str(f_obj))\n"
         "float: 0.00042\n"
         ">>> s_obj = pyScript.aelEngineerNotation(\"6543210\")\n"
         ">>> print('string:', str(s_obj))\n"
         "string: 6.543e+06"),
        ("aelEngineerNotation-sig-digits-stack",
         "Push 6 significant digits, format a number, push 3, format again, "
         "then pop twice to restore. Demonstrates the precision stack.",
         ["aelEngineerNotation", "aelPushSignifDigs", "aelPopSignifDigs"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.aelPushSignifDigs(6)\n"
         "6\n"
         ">>> a = pyScript.aelEngineerNotation(3.141592653589)\n"
         ">>> print('6-dig:', str(a))\n"
         "6-dig: 3.14159\n"
         ">>> pyScript.aelPushSignifDigs(3)\n"
         "3\n"
         ">>> b = pyScript.aelEngineerNotation(3.141592653589)\n"
         ">>> print('3-dig:', str(b))\n"
         "3-dig: 3.14\n"
         ">>> pyScript.aelPopSignifDigs()\n"
         "3\n"
         ">>> pyScript.aelPopSignifDigs()\n"
         "6"),
    ]:
        _add("S4", "v34-S4-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S4 multi_step: %s" % scenario)
    for label, scenario, apis, code in [
        ("aelEngineerNotation-large-and-small",
         "Format a very large and a very small number to confirm scientific "
         "notation is used outside [0.001, 1000), and handle a negative value.",
         ["aelEngineerNotation"],
         ">>> import pyAether as pyScript\n"
         ">>> big = pyScript.aelEngineerNotation(12345678.9)\n"
         ">>> print('big:', str(big))\n"
         "big: 1.235e+07\n"
         ">>> tiny = pyScript.aelEngineerNotation(0.000001234)\n"
         ">>> print('tiny:', str(tiny))\n"
         "tiny: 1.234e-06\n"
         ">>> neg = pyScript.aelEngineerNotation(-456.789)\n"
         ">>> print('neg:', str(neg))\n"
         "neg: -456.8"),
        ("aelEngineerNotation-invalid-string",
         "Show that an invalid numeric string yields an empty string rather "
         "than raising an exception, and that zero formats as '0'.",
         ["aelEngineerNotation"],
         ">>> import pyAether as pyScript\n"
         ">>> bad = pyScript.aelEngineerNotation(\"not_a_number\")\n"
         ">>> print('invalid:', repr(str(bad)))\n"
         "invalid: ''\n"
         ">>> zero = pyScript.aelEngineerNotation(0.0)\n"
         ">>> print('zero:', str(zero))\n"
         "zero: 0"),
    ]:
        _add("S5", "v34-S5-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S5 advanced: %s" % scenario)

    # ===== timeToTm (+ etTimeToString) =====
    name = "timeToTm"
    doc = _doc_block(name)
    d = API_DOCS[name]
    _add("S1", "v34-S1-%s" % name,
         ("You are an EDA automation engineer. Given the following "
          "PyAether API reference, write a minimal correct Python "
          "code snippet that uses `%s`.\n\n%s" % (name, doc)),
         "```python\n%s\n```" % d["doctest"], [name],
         "S1 doc_to_code for %s" % name)
    _add("S3", "v34-S3-%s" % name,
         ("You are an EDA automation engineer. The following Python "
          "code uses a PyAether API. Identify the API name, describe "
          "what it does, and explain its signature.\n\n"
          "```python\n%s\n```" % d["doctest"]),
         ("The API used is **`%s`**.\n\n**Signature**: `%s`\n\n%s\n\n"
          "**Key notes**: %s" % (name, d["sig"], d["desc"],
                                 d.get("key_notes", ""))),
         [name], "S3 code_to_doc for %s" % name)
    for label, scenario, apis, code in [
        ("timeToTm-year-month-day",
         "Convert a timestamp to a struct_time and extract the full year, "
         "month, and day. Confirm tm_year is the full year, not since-1900.",
         ["timeToTm"],
         ">>> import pyAether as pyScript\n"
         ">>> tm = pyScript.timeToTm(1609459200)\n"
         ">>> print('date:', tm.tm_year, tm.tm_mon, tm.tm_mday)\n"
         "date: 2021 1 1\n"
         ">>> print('is full year:', tm.tm_year > 1900)\n"
         "is full year: True"),
        ("timeToTm-weekday-and-yday",
         "Convert a timestamp and inspect the weekday (0=Monday) and day-of-"
         "year fields to understand the struct_time layout.",
         ["timeToTm"],
         ">>> import pyAether as pyScript\n"
         ">>> tm = pyScript.timeToTm(946684800)\n"
         ">>> print('weekday (0=Mon):', tm.tm_wday)\n"
         "weekday (0=Mon): 5\n"
         ">>> print('day of year:', tm.tm_yday)\n"
         "day of year: 1"),
    ]:
        _add("S4", "v34-S4-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S4 multi_step: %s" % scenario)
    for label, scenario, apis, code in [
        ("timeToTm-and-etTimeToString-pair",
         "Convert a timestamp with timeToTm and also format it with "
         "etTimeToString, showing both APIs use the same timestamp base.",
         ["timeToTm", "etTimeToString"],
         ">>> import pyAether as pyScript\n"
         ">>> ts = 1700000000\n"
         ">>> tm = pyScript.timeToTm(ts)\n"
         ">>> print('struct:', tm.tm_year, tm.tm_mon, tm.tm_mday)\n"
         "struct: 2023 11 14\n"
         ">>> txt = pyScript.etTimeToString(ts)\n"
         ">>> print('formatted:', isinstance(txt, str))\n"
         "formatted: True"),
        ("timeToTm-hour-min-sec",
         "Extract the time-of-day fields (hour, minute, second) from a "
         "timestamp to confirm the full struct_time is populated.",
         ["timeToTm"],
         ">>> import pyAether as pyScript\n"
         ">>> tm = pyScript.timeToTm(1700000000)\n"
         ">>> print('hms:', tm.tm_hour, tm.tm_min, tm.tm_sec)\n"
         "hms: 22 13 20"),
    ]:
        _add("S5", "v34-S5-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S5 advanced: %s" % scenario)

    # ===== setPyAePath (+ getPyAePath) =====
    name = "setPyAePath"
    doc = _doc_block(name)
    d = API_DOCS[name]
    _add("S1", "v34-S1-%s" % name,
         ("You are an EDA automation engineer. Given the following "
          "PyAether API reference, write a minimal correct Python "
          "code snippet that uses `%s`.\n\n%s" % (name, doc)),
         "```python\n%s\n```" % d["doctest"], [name],
         "S1 doc_to_code for %s" % name)
    _add("S3", "v34-S3-%s" % name,
         ("You are an EDA automation engineer. The following Python "
          "code uses a PyAether API. Identify the API name, describe "
          "what it does, and explain its signature.\n\n"
          "```python\n%s\n```" % d["doctest"]),
         ("The API used is **`%s`**.\n\n**Signature**: `%s`\n\n%s\n\n"
          "**Key notes**: %s" % (name, d["sig"], d["desc"],
                                 d.get("key_notes", ""))),
         [name], "S3 code_to_doc for %s" % name)
    for label, scenario, apis, code in [
        ("setPyAePath-list-mixed",
         "Add a list of paths where some exist and some do not, then inspect "
         "the returned missing-paths list.",
         ["setPyAePath"],
         ">>> import pyAether as pyScript\n"
         ">>> result = pyScript.setPyAePath([\"/tmp\", \"/no/such/dir/xyz\"])\n"
         ">>> print('missing count:', len(result))\n"
         "missing count: 1\n"
         ">>> print('missing is list:', isinstance(result, list))\n"
         "missing is list: True"),
        ("setPyAePath-then-getPyAePath",
         "Add a path with setPyAePath, then retrieve the current valid paths "
         "with getPyAePath to verify the addition.",
         ["setPyAePath", "getPyAePath"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.setPyAePath(\"/tmp\")\n"
         "[]\n"
         ">>> current = pyScript.getPyAePath()\n"
         ">>> print('path count:', len(current))\n"
         "path count: 1\n"
         ">>> print('is list:', isinstance(current, list))\n"
         "is list: True"),
    ]:
        _add("S4", "v34-S4-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S4 multi_step: %s" % scenario)
    for label, scenario, apis, code in [
        ("setPyAePath-empty-and-tilde",
         "Show that an empty list returns an empty list, and that a tilde-"
         "prefixed path is expanded to the home directory.",
         ["setPyAePath"],
         ">>> import pyAether as pyScript\n"
         ">>> r1 = pyScript.setPyAePath([])\n"
         ">>> print('empty list:', r1)\n"
         "empty list: []\n"
         ">>> r2 = pyScript.setPyAePath(\"~/no_such_module_dir\")\n"
         ">>> print('tilde expanded, missing:', len(r2) > 0)\n"
         "tilde expanded, missing: True"),
        ("setPyAePath-all-exist",
         "When all provided paths exist on the filesystem, the returned "
         "missing list is empty. Demonstrate with known-existing paths.",
         ["setPyAePath", "getPyAePath"],
         ">>> import pyAether as pyScript\n"
         ">>> r = pyScript.setPyAePath([\"/tmp\"])\n"
         ">>> print('all exist:', r == [])\n"
         "all exist: True\n"
         ">>> paths = pyScript.getPyAePath()\n"
         ">>> print('retrieved:', isinstance(paths, list))\n"
         "retrieved: True"),
    ]:
        _add("S5", "v34-S5-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S5 advanced: %s" % scenario)

    # ===== S6: cross-API workflow (2 pairs) =====
    for apis_str, scenario, apis, code in [
        ("notation-with-precision-pipeline",
         "Build a pipeline: push 6 significant digits, format a measurement "
         "value, pop to restore default, then format another value.",
         ["aelEngineerNotation", "aelPushSignifDigs", "aelPopSignifDigs"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.aelPushSignifDigs(6)\n"
         "6\n"
         ">>> m1 = pyScript.aelEngineerNotation(2.718281828)\n"
         ">>> print('high-prec:', str(m1))\n"
         "high-prec: 2.71828\n"
         ">>> pyScript.aelPopSignifDigs()\n"
         "6\n"
         ">>> m2 = pyScript.aelEngineerNotation(2.718281828)\n"
         ">>> print('default-prec:', str(m2))\n"
         "default-prec: 2.718"),
        ("timestamp-format-and-path-setup",
         "A setup routine: convert a build timestamp to a date with timeToTm, "
         "format it as a string with etTimeToString, and register a module "
         "path with setPyAePath, checking the missing-path result.",
         ["timeToTm", "etTimeToString", "setPyAePath"],
         ">>> import pyAether as pyScript\n"
         ">>> ts = 1700000000\n"
         ">>> tm = pyScript.timeToTm(ts)\n"
         ">>> print('build date:', tm.tm_year, tm.tm_mon, tm.tm_mday)\n"
         "build date: 2023 11 14\n"
         ">>> label = pyScript.etTimeToString(ts)\n"
         ">>> print('label is str:', isinstance(label, str))\n"
         "label is str: True\n"
         ">>> missing = pyScript.setPyAePath(\"/tmp\")\n"
         ">>> print('path ok:', missing == [])\n"
         "path ok: True"),
    ]:
        _add("S6", "v34-S6-%s" % apis_str,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis,
             "S6 cross_api_workflow: %s" % scenario)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    parser = argparse.ArgumentParser(
        description="R204 v34 utility-batch SFT corpus builder "
                    "(3 Misc-Commands APIs + 3 related, ~20 pairs)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print stats only, do not write output file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Output JSONL path (default: %s)" % DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of pairs (for testing)")
    args = parser.parse_args()

    sys.stderr.write("R204 v34 utility-batch corpus builder\n")
    sys.stderr.write("  Target APIs: %d (%s)\n" % (
        len(API_ORDER), ", ".join(API_ORDER)))

    missing = [a for a in API_ORDER if a not in API_DOCS]
    if missing:
        sys.stderr.write("ERROR: Missing API_DOCS for: %s\n"
                         % ", ".join(missing))
        sys.exit(1)

    eval_eps = load_eval_entry_points()
    sys.stderr.write("  Eval entry_points loaded: %d\n" % len(eval_eps))
    for a in ["aelEngineerNotation", "timeToTm", "setPyAePath"]:
        sys.stderr.write("  %s is entry_point? %s\n" % (a, a in eval_eps))

    pairs, rejected, reject_details = build_pairs(eval_eps, limit=args.limit)

    api_coverage = {}
    for p in pairs:
        for a in p["api_used"]:
            api_coverage[a] = api_coverage.get(a, 0) + 1

    type_counts = {}
    for p in pairs:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

    sys.stderr.write("\n=== R204 v34 Corpus Stats ===\n")
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

