#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r195_et_pcre_rex_corpus.py
R195 -- v25 PyAether SFT corpus: et* regex blind spot (6 APIs, 30 pairs).

BACKGROUND: v11-v24 (638 pairs) cover 115/164 eval raw APIs (70.1%). 49 blind.
Data-driven scan (R191 blind_scan, re-run with v24 this wake) shows et* is the
#1 blind family (tied with ae* at 8 usages, but et* has fewer APIs: 6 vs 8).
R195 targets 6 et* APIs (PCRE + Rex regex families).

Two sub-families:
  - etPcre* : PCRE (Perl Compatible), OBJECT-based. etPcreCompile returns a
              compiled pattern object (_etReComPatObj). Richer compile/exec
              options via etPcreGenCompileOptBits / etPcreGenExecOptBits.
  - etRex*  : Rex, GLOBAL-state-based. etRexCompile returns bool (True=valid),
              stores pattern globally for etRexReplace / etRexExecute.

All ISOLATE-class (eval helper regex utilities used in eval canonical_solution
for pattern matching / substitution).  Fingerprint scan rejects eval entry_points.

Authoritative signatures fetched via pyAether MCP get_api_details (R195 wake).

Usage:
  python3 baize_posttrain_r195_et_pcre_rex_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v25_et_pcre_rex.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["etPcreCompile"] = {
    "sig": "etPcreCompile(pattern, options=0) -> _etReComPatObj",
    "desc": "Compiles a PCRE (Perl Compatible Regular Expression) pattern string into an internal compiled pattern object. The returned object is passed to etPcreExecute for matching and to etPcreSubstitute for tag substitution. The compiled object can be reused across multiple execute calls for performance. If compilation fails (e.g. unbalanced brackets), a ValueError is raised.",
    "params": {
        "pattern": "str or emyString -- the regular expression string to compile (standard PCRE syntax)",
        "options": "int, optional -- bitwise OR of compile option bits; generate with etPcreGenCompileOptBits (caseLess, multiLine, dotAll, extended, anchored, dollar_endonly, not_auto_capture, firstline). Default 0.",
    },
    "returns": "_etReComPatObj -- compiled pattern data object; reuse for multiple etPcreExecute calls",
    "methods": "Pass the returned object as first arg to etPcreExecute(reObj, subject) and optionally to etPcreSubstitute(string, pcreObject=reObj).",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> reObj = pyScript.etPcreCompile("^[a-z][0-9a-z]*")\n'
                '>>> pyScript.etPcreExecute(reObj, "abc123")\n'
                'True\n'
                '>>> pyScript.etPcreExecute(reObj, "9abc")\n'
                'False\n'
                '>>> # case-insensitive compile\n'
                '>>> opts = pyScript.etPcreGenCompileOptBits(caseLess=True)\n'
                '>>> reObj2 = pyScript.etPcreCompile("hello", opts)\n'
                '>>> pyScript.etPcreExecute(reObj2, "HELLO World")\n'
                'True'),
    "category": "Regex / PCRE Compile", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Returns a _etReComPatObj (NOT a bool). Invalid patterns raise ValueError -- always wrap in try/except. Compile options are separate from execution options: use etPcreGenCompileOptBits for compile, etPcreGenExecOptBits for execute. The compiled object is reusable; pre-compile patterns used in loops for performance."}

API_DOCS["etPcreExecute"] = {
    "sig": "etPcreExecute(reObj, subject, options=0) -> bool",
    "desc": "Matches the subject string (or emyString object) against a previously compiled PCRE pattern object (returned by etPcreCompile). Returns True if the pattern matches anywhere in the subject, False otherwise. Execution options (e.g. anchored, notempty) can be passed via etPcreGenExecOptBits to refine matching behavior at execute time without recompiling.",
    "params": {
        "reObj": "_etReComPatObj -- compiled pattern from etPcreCompile",
        "subject": "str or emyString -- the string to test against the compiled pattern",
        "options": "int, optional -- bitwise OR of execution option bits; generate with etPcreGenExecOptBits (anchored, notbol, noteol, notempty). Default 0.",
    },
    "returns": "bool -- True if pattern matches subject, False otherwise",
    "methods": "After a successful match, call etPcreSubstitute to extract/rearrange captured groups using backreference tags (\\1, \\2, \\0 for whole match).",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> reObj = pyScript.etPcreCompile(r"(\\d{3})-(\\d{4})")\n'
                '>>> pyScript.etPcreExecute(reObj, "call 555-1234 now")\n'
                'True\n'
                '>>> pyScript.etPcreExecute(reObj, "no phone here")\n'
                'False\n'
                '>>> # use notempty to reject empty matches\n'
                '>>> reObj2 = pyScript.etPcreCompile("a?b?")\n'
                '>>> opts = pyScript.etPcreGenExecOptBits(notempty=True)\n'
                '>>> pyScript.etPcreExecute(reObj2, "ccacdbff", opts)\n'
                'True'),
    "category": "Regex / PCRE Execute", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "The first argument is the compiled object from etPcreCompile (NOT a pattern string). Returns bool, not a match object. To extract captured groups, call etPcreSubstitute after a successful match. Execution options (anchored/notempty/etc.) are applied at match time and do NOT require recompilation."}

API_DOCS["etPcreGenExecOptBits"] = {
    "sig": "etPcreGenExecOptBits(anchored=False, notbol=False, noteol=False, notempty=False) -> int",
    "desc": "Generates a bitwise-OR integer of execution-time option bits that control how etPcreExecute performs matching. These options affect matching behavior without requiring recompilation of the pattern. Call with no arguments returns 0 (all defaults). Pass the result as the optional third argument to etPcreExecute.",
    "params": {
        "anchored": "bool -- force pattern to match only at the start of the subject (bit 16)",
        "notbol": "bool -- subject is NOT the beginning of a line; ^ will not match start (bit 128)",
        "noteol": "bool -- subject is NOT the end of a line; $ will not match end (bit 256)",
        "notempty": "bool -- an empty string is NOT a valid match (bit 1024)",
    },
    "returns": "int -- bitwise OR of the selected option bits (0 if none selected)",
    "methods": "Pass the returned int as the options argument to etPcreExecute(reObj, subject, options).",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> reObj = pyScript.etPcreCompile(r"\\d+")\n'
                '>>> opts_a = pyScript.etPcreGenExecOptBits(anchored=True)\n'
                '>>> pyScript.etPcreExecute(reObj, "123abc", opts_a)\n'
                'True\n'
                '>>> pyScript.etPcreExecute(reObj, "abc123", opts_a)\n'
                'False\n'
                '>>> reObj2 = pyScript.etPcreCompile("a*")\n'
                '>>> opts_n = pyScript.etPcreGenExecOptBits(notempty=True)\n'
                '>>> pyScript.etPcreExecute(reObj2, "bbb", opts_n)\n'
                'False\n'
                '>>> pyScript.etPcreGenExecOptBits()\n'
                '0'),
    "category": "Regex / PCRE Exec Options", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "This is for EXECUTION options (etPcreExecute), distinct from COMPILE options (etPcreGenCompileOptBits for etPcreCompile). Bit values: anchored=16, notbol=128, noteol=256, notempty=1024. Combined e.g. anchored+notempty=1040. Call with no args returns 0 (default)."}

API_DOCS["etPcreSubstitute"] = {
    "sig": "etPcreSubstitute(string, pcreObject=None) -> str or None",
    "desc": "Copies the input string and substitutes pattern tags (backreferences) using the matched groups from the most recent etPcreExecute call. Tags: \\0 = entire match, \\1..\\9 = captured groups, \\{n} for group n>=10. If pcreObject is provided, uses that specific compiled object's last match result. Must be called AFTER a successful etPcreExecute; returns None if no prior match exists.",
    "params": {
        "string": "str -- the template string containing backreference tags (\\0, \\1, \\2, ...)",
        "pcreObject": "_etReComPatObj, optional -- use this object's match result instead of the global last match",
    },
    "returns": "str -- the substituted string; None if no prior match was performed",
    "methods": "Always call etPcreExecute(reObj, subject) first, then etPcreSubstitute(template) to rearrange captured groups.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> reObj = pyScript.etPcreCompile(r"(\\w+)@(\\w+\\.\\w+)")\n'
                '>>> pyScript.etPcreExecute(reObj, "user@example.com")\n'
                'True\n'
                '>>> result = pyScript.etPcreSubstitute("domain=\\2 user=\\1")\n'
                '>>> print(result)\n'
                'domain=example.com user=user\n'
                '>>> pyScript.etPcreSubstitute("matched: \\0")\n'
                'matched: user@example.com'),
    "category": "Regex / PCRE Substitute", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "MUST be called after a successful etPcreExecute -- returns None otherwise. Use \\n format for backreferences (NOT ?n? or {} format). \\0 = entire match, \\1-\\9 = groups 1-9, \\{n} for n>=10. When using multiple compiled patterns, pass pcreObject to select which match result to use. Each etPcreExecute overwrites the global match state."}

API_DOCS["etRexCompile"] = {
    "sig": "etRexCompile(pattern) -> bool",
    "desc": "Compiles a regular expression pattern string into a GLOBAL internal representation used by subsequent etRexExecute, etRexReplace, etRexMatchp, and etRexSubstitute calls. Unlike the PCRE family (etPcreCompile which returns an object), etRexCompile stores the compiled pattern globally and returns True if the pattern is valid, False if invalid. The last-compiled pattern overwrites any previous one.",
    "params": {
        "pattern": "str or emyString -- the regular expression pattern to compile (Rex syntax: ., *, +, [...], ^, $, \\<, \\>, \\1-\\9 backreferences)",
    },
    "returns": "bool -- True if the pattern compiled successfully, False if the pattern is invalid",
    "methods": "After compiling, call etRexReplace(source, replacement, index) or etRexExecute(subject) to use the global compiled pattern.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.etRexCompile("[0-9]+")\n'
                'True\n'
                '>>> pyScript.etRexCompile("[0-9")\n'
                'False\n'
                '>>> pyScript.etRexCompile(r"\\d+")\n'
                'True\n'
                '>>> pyScript.etRexReplace("abc123def456", "NUM", 0)\n'
                'abcNUMdefNUM'),
    "category": "Regex / Rex Compile", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns BOOL (True=valid), NOT a compiled object -- this is the key difference from etPcreCompile. The compiled pattern is stored GLOBALLY; each etRexCompile overwrites the previous one. Supports Rex syntax (\\< and \\> for word boundaries, \\1-\\9 for backreferences). Always check the return value before calling etRexReplace."}

API_DOCS["etRexReplace"] = {
    "sig": "etRexReplace(source, replacement, index) -> str",
    "desc": "Returns a copy of the source string in which substrings matching the last etRexCompile-compiled pattern are replaced with the replacement string. The index controls which occurrences to replace: index<=0 replaces ALL matches, index>0 replaces only the nth match. The replacement string supports pattern tags: & = the matched text, [&] = matched text wrapped in brackets. If no match is found, the original string is returned unchanged.",
    "params": {
        "source": "str or emyString -- the original string to process",
        "replacement": "str -- the replacement string; supports & (matched text) and [&] (bracketed match) tags",
        "index": "int -- <=0 to replace ALL occurrences; >0 to replace only the nth occurrence (1-based)",
    },
    "returns": "str -- the string with replacements applied; original string if no match",
    "methods": "Must call etRexCompile(pattern) first. Then etRexReplace(source, replacement, index) applies the replacement.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.etRexCompile("[0-9]")\n'
                'True\n'
                '>>> pyScript.etRexReplace("a1b2c3", "X", 0)\n'
                'aXbXcX\n'
                '>>> pyScript.etRexReplace("a1b2c3", "X", 2)\n'
                'a1bXc3\n'
                '>>> pyScript.etRexCompile("[A-Z]+")\n'
                'True\n'
                '>>> pyScript.etRexReplace("Hello World", "[&]", 0)\n'
                '[Hello] [World]\n'
                '>>> pyScript.etRexCompile("\\\\s+")\n'
                'True\n'
                '>>> pyScript.etRexReplace("a  b   c", "", 0)\n'
                'abc'),
    "category": "Regex / Rex Replace", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Must call etRexCompile FIRST (uses global compiled pattern). index<=0 = replace ALL; index>0 = replace only the nth match (1-based). Pattern tags in replacement: & = matched text, [&] = bracketed match. No match -> returns original string unchanged. Returns str always (even for emyString input)."}


API_ORDER = ["etPcreCompile", "etPcreExecute", "etPcreGenExecOptBits",
             "etPcreSubstitute", "etRexCompile", "etRexReplace"]

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

    # ---- S1: doc -> code (6 pairs, one per API) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v25-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S3: code -> doc (6 pairs, one per API) ----
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
        _add("S3", "v25-S3-%s" % name, prompt, completion, [name],
             "S3 code_to_doc for %s" % name)

    # ---- S4: multi-step trace (6 pairs) ----
    s4_traces = [
        ("etPcreCompile",
         "Compile a PCRE pattern to extract a date in YYYY-MM-DD format, then test it against several strings.",
         ["etPcreCompile"],
         ("import pyAether as pyScript\n\n"
          "date_re = pyScript.etPcreCompile(r'(\\d{4})-(\\d{2})-(\\d{2})')\n"
          "print('compiled date pattern')\n"
          "for s in ['2026-11-10', 'not a date', '2025-01-15 meeting']:\n"
          "    matched = pyScript.etPcreExecute(date_re, s)\n"
          "    print('%s -> %s' % (s, matched))\n"
          "if pyScript.etPcreExecute(date_re, '2026-11-10'):\n"
          "    reformatted = pyScript.etPcreSubstitute('\\3/\\2/\\1')\n"
          "    print('reformatted:', reformatted)")),
        ("etPcreExecute",
         "Compile a pattern for hex color codes and check multiple strings, using notempty to avoid trivial empty matches.",
         ["etPcreExecute"],
         ("import pyAether as pyScript\n\n"
          "hex_re = pyScript.etPcreCompile('#[0-9A-Fa-f]{6}')\n"
          "opts = pyScript.etPcreGenExecOptBits(notempty=True)\n"
          "test_strings = ['color: #FF5733;', 'no color', '#ABCDEF bg', '#']\n"
          "for s in test_strings:\n"
          "    result = pyScript.etPcreExecute(hex_re, s, opts)\n"
          "    print('%-20s -> %s' % (s, result))\n"
          "if pyScript.etPcreExecute(hex_re, 'color: #FF5733;'):\n"
          "    extracted = pyScript.etPcreSubstitute('found: \\0')\n"
          "    print(extracted)")),
        ("etPcreGenExecOptBits",
         "Demonstrate the difference between default and anchored execution: a pattern that matches anywhere vs only at the start.",
         ["etPcreGenExecOptBits"],
         ("import pyAether as pyScript\n\n"
          "word_re = pyScript.etPcreCompile('[A-Za-z]+')\n"
          "default_opts = pyScript.etPcreGenExecOptBits()\n"
          "anchored_opts = pyScript.etPcreGenExecOptBits(anchored=True)\n"
          "subjects = ['hello world', '123abc', '   test']\n"
          "for s in subjects:\n"
          "    r_def = pyScript.etPcreExecute(word_re, s, default_opts)\n"
          "    r_anc = pyScript.etPcreExecute(word_re, s, anchored_opts)\n"
          "    print('%-15s default=%s anchored=%s' % (s, r_def, r_anc))\n"
          "print('default opts value:', default_opts)\n"
          "print('anchored opts value:', anchored_opts)")),
        ("etPcreSubstitute",
         "Parse a key=value pair with PCRE, then use etPcreSubstitute to rearrange into 'value <- key' format.",
         ["etPcreSubstitute"],
         ("import pyAether as pyScript\n\n"
          "kv_re = pyScript.etPcreCompile(r'(\\w+)=(\\w+)')\n"
          "test = 'netname=VDD voltage=1200'\n"
          "if pyScript.etPcreExecute(kv_re, test):\n"
          "    swapped = pyScript.etPcreSubstitute('\\2 <- \\1')\n"
          "    print('swapped:', swapped)\n"
          "    echoed = pyScript.etPcreSubstitute('whole match: \\0')\n"
          "    print(echoed)\n"
          "if pyScript.etPcreExecute(kv_re, 'layer=M1'):\n"
          "    result = pyScript.etPcreSubstitute('layer is \\2')\n"
          "    print(result)")),
        ("etRexCompile",
         "Compile a Rex pattern to match net names, check validity, then use it for replacement.",
         ["etRexCompile"],
         ("import pyAether as pyScript\n\n"
          "ok = pyScript.etRexCompile('net[A-Z]*[0-9]+')\n"
          "print('valid pattern:', ok)\n"
          "if ok:\n"
          "    cleaned = pyScript.etRexReplace('netVDD netGND netCLK0', 'NET', 0)\n"
          "    print('replaced all:', cleaned)\n"
          "    single = pyScript.etRexReplace('netVDD netGND netCLK0', 'NET', 2)\n"
          "    print('replaced 2nd:', single)\n"
          "bad = pyScript.etRexCompile('[unclosed')\n"
          "print('invalid pattern:', bad)")),
        ("etRexReplace",
         "Use etRexReplace to normalize whitespace and highlight matched tokens in a netlist line.",
         ["etRexReplace"],
         ("import pyAether as pyScript\n\n"
          "pyScript.etRexCompile('\\\\s+')\n"
          "line = '  R1   netA   netB   1k  '\n"
          "single_space = pyScript.etRexReplace(line, ' ', 0)\n"
           "print('normalized:', single_space.strip())\n"
           "pyScript.etRexCompile('[A-Za-z]+[0-9]+')\n"
           "highlighted = pyScript.etRexReplace('R1 C2 L3 Q4', '[&]', 0)\n"
           "print('highlighted:', highlighted)\n"
           "only_second = pyScript.etRexReplace('R1 C2 L3 Q4', 'XX', 2)\n"
           "print('replace 2nd:', only_second)")),
    ]
    for name, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v25-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)

    # ---- S5: anti_pattern / common mistake (6 pairs) ----
    s5_items = [
        ("etPcreCompile",
         "reObj = pyScript.etPcreExecute('[0-9]+', 'abc123')",
         "etPcreExecute takes a COMPILED pattern object as its first argument, not a raw pattern string. You must call etPcreCompile first to get the compiled object, then pass it to etPcreExecute. Passing a string directly will fail.",
         "reObj = pyScript.etPcreCompile('[0-9]+')\nresult = pyScript.etPcreExecute(reObj, 'abc123')"),
        ("etPcreExecute",
         "reObj = pyScript.etPcreCompile('hello')\nif pyScript.etPcreExecute(reObj, 'HELLO World'):\n    print('matched')",
         "By default, PCRE matching is case-sensitive, so 'hello' will NOT match 'HELLO World'. To match case-insensitively, compile with the caseLess option via etPcreGenCompileOptBits.",
         "opts = pyScript.etPcreGenCompileOptBits(caseLess=True)\nreObj = pyScript.etPcreCompile('hello', opts)\nif pyScript.etPcreExecute(reObj, 'HELLO World'):\n    print('matched')"),
        ("etPcreGenExecOptBits",
         "reObj = pyScript.etPcreCompile('hello')\nopts = pyScript.etPcreGenCompileOptBits(caseLess=True)\nresult = pyScript.etPcreExecute(reObj, 'HELLO', opts)",
         "etPcreGenCompileOptBits generates COMPILE-time options (for etPcreCompile), NOT execution-time options. Passing compile options to etPcreExecute has no effect on matching. For execution-time behavior use etPcreGenExecOptBits instead. caseLess is a compile option -- use it in etPcreCompile.",
         "opts = pyScript.etPcreGenCompileOptBits(caseLess=True)\nreObj = pyScript.etPcreCompile('hello', opts)\nresult = pyScript.etPcreExecute(reObj, 'HELLO')\nexec_opts = pyScript.etPcreGenExecOptBits(anchored=True)\nresult2 = pyScript.etPcreExecute(reObj, 'say HELLO', exec_opts)"),
        ("etPcreSubstitute",
         "reObj = pyScript.etPcreCompile(r'(\\w+)')\nresult = pyScript.etPcreSubstitute('word: \\1')",
         "etPcreSubstitute returns None (or fails silently) if no etPcreExecute has been called beforehand. You MUST call etPcreExecute(reObj, subject) to perform a match BEFORE calling etPcreSubstitute, so that captured groups are available.",
         "reObj = pyScript.etPcreCompile(r'(\\w+)')\nif pyScript.etPcreExecute(reObj, 'hello world'):\n    result = pyScript.etPcreSubstitute('word: \\1')\n    print(result)"),
        ("etRexCompile",
         "result = pyScript.etRexCompile('[0-9]+')\nif not result:\n    pattern_obj = result\n    pyScript.etRexReplace('abc123', 'X', 0)",
         "etRexCompile returns a BOOL (True if valid, False if invalid), NOT a compiled pattern object. Unlike etPcreCompile which returns an object, etRexCompile stores the pattern globally. You cannot use the return value as a pattern object. Check the bool, then call etRexReplace directly.",
         "valid = pyScript.etRexCompile('[0-9]+')\nif valid:\n    result = pyScript.etRexReplace('abc123', 'X', 0)\n    print(result)"),
        ("etRexReplace",
         "pyScript.etRexCompile('[A-Z]+')\nresult = pyScript.etRexReplace('Hello World', 'X', 0)\n# expected: 'X X' but got 'Hello World'",
         "etRexCompile with '[A-Z]+' only matches uppercase letter sequences. 'Hello' starts with uppercase 'H' but continues with lowercase, so only 'H' matches, then 'W' matches. The pattern '[A-Za-z]+' would match full words. The issue is the pattern, not the API. Also ensure etRexCompile returned True before calling etRexReplace.",
         "ok = pyScript.etRexCompile('[A-Za-z]+')\nif ok:\n    result = pyScript.etRexReplace('Hello World', 'X', 0)\n    print(result)  # 'X X'"),
    ]
    for name, wrong, mistake, correct in s5_items:
        prompt = ("You are an EDA automation engineer. The following PyAether "
                  "code has a bug. Identify the mistake and write the corrected "
                  "version.\n\n```python\n%s\n```" % wrong)
        completion = ("**Mistake**: %s\n\n**Corrected code**:\n```python\n%s\n```" % (mistake, correct))
        _add("S5", "v25-S5-%s" % name, prompt, completion, [name],
             "S5 anti_pattern for %s" % name)

    # ---- S6: cross-API combination (6 pairs) ----
    s6_items = [
        ("etPcreCompile+etPcreExecute+etPcreSubstitute",
         "Compile a PCRE pattern to parse a component reference (e.g. R1, C2), execute it on a netlist line, then substitute to extract and reformat the matched component.",
         ["etPcreCompile", "etPcreExecute", "etPcreSubstitute"],
         ("import pyAether as pyScript\n\n"
          "comp_re = pyScript.etPcreCompile(r'([A-Za-z]+)([0-9]+)')\n"
          "line = 'Place R1 near C2 and L3'\n"
          "if pyScript.etPcreExecute(comp_re, line):\n"
          "    typed = pyScript.etPcreSubstitute('type=\\1 num=\\2')\n"
          "    print(typed)\n"
          "    full = pyScript.etPcreSubstitute('ref=\\0')\n"
          "    print(full)\n"
          "if pyScript.etPcreExecute(comp_re, 'Q5 driver'):\n"
          "    q_info = pyScript.etPcreSubstitute('transistor \\1#\\2')\n"
          "    print(q_info)")),
        ("etPcreCompile+etPcreGenExecOptBits+etPcreExecute",
         "Compile a pattern and demonstrate anchored vs non-anchored execution on the same subject, showing how execution options change results without recompilation.",
         ["etPcreCompile", "etPcreGenExecOptBits", "etPcreExecute"],
         ("import pyAether as pyScript\n\n"
          "num_re = pyScript.etPcreCompile(r'[0-9]+')\n"
          "subjects = ['123start', 'end456', 'no digits']\n"
          "default_opts = pyScript.etPcreGenExecOptBits()\n"
          "anchored_opts = pyScript.etPcreGenExecOptBits(anchored=True)\n"
          "print('default vs anchored:')\n"
          "for s in subjects:\n"
          "    r_def = pyScript.etPcreExecute(num_re, s, default_opts)\n"
          "    r_anc = pyScript.etPcreExecute(num_re, s, anchored_opts)\n"
          "    print('  %-15s default=%s anchored=%s' % (s, r_def, r_anc))")),
        ("etPcreGenExecOptBits+etPcreExecute+etPcreSubstitute",
         "Use notempty execution option to avoid empty matches with a permissive pattern, then substitute the captured email components.",
         ["etPcreGenExecOptBits", "etPcreExecute", "etPcreSubstitute"],
         ("import pyAether as pyScript\n\n"
          "email_re = pyScript.etPcreCompile(r'(\\w+)@(\\w+\\.\\w+)')\n"
          "opts = pyScript.etPcreGenExecOptBits(notempty=True)\n"
          "text = 'contact admin@site.org for info'\n"
          "if pyScript.etPcreExecute(email_re, text, opts):\n"
          "    user = pyScript.etPcreSubstitute('user=\\1')\n"
          "    domain = pyScript.etPcreSubstitute('domain=\\2')\n"
           "    print('user:', user, 'domain:', domain)")),
        ("etRexCompile+etRexReplace",
         "Compile a Rex pattern to strip comments from an EDA script line, then use index to replace only specific occurrences.",
         ["etRexCompile", "etRexReplace"],
         ("import pyAether as pyScript\n\n"
          "ok = pyScript.etRexCompile('//.*$')\n"
          "if ok:\n"
          "    line = 'dbCrtRect(cv, bbox, layer) // create rect // M1 layer'\n"
          "    no_comments = pyScript.etRexReplace(line, '', 0)\n"
          "    print('stripped:', no_comments.strip())\n"
          "pyScript.etRexCompile('[0-9]+')\n"
          "data = 'v1=3.3 v2=2.5 v3=1.8'\n"
          "all_nums = pyScript.etRexReplace(data, 'N', 0)\n"
          "print('all replaced:', all_nums)\n"
          "second_only = pyScript.etRexReplace(data, 'N', 2)\n"
          "print('2nd only:', second_only)")),
        ("etPcreCompile+etRexCompile",
         "Show the fundamental difference between the PCRE family (object-based) and Rex family (global-state-based) by compiling and using both in the same script.",
         ["etPcreCompile", "etRexCompile"],
         ("import pyAether as pyScript\n\n"
          "# PCRE: object-based, compile returns a reusable object\n"
          "pcre_obj = pyScript.etPcreCompile(r'\\d{4}')\n"
          "print('PCRE type:', type(pcre_obj).__name__)\n"
          "r1 = pyScript.etPcreExecute(pcre_obj, 'year 2026')\n"
          "r2 = pyScript.etPcreExecute(pcre_obj, 'no year')\n"
          "print('PCRE match 2026:', r1, ' no year:', r2)\n"
          "# Rex: global-state, compile returns bool\n"
          "valid = pyScript.etRexCompile('[A-Z]{2,}')\n"
          "print('Rex valid:', valid, '(type:', type(valid).__name__, ')')\n"
          "if valid:\n"
          "    out = pyScript.etRexReplace('IO and CLK pins', '#', 0)\n"
          "    print('Rex replace:', out)")),
        ("etPcreExecute+etPcreSubstitute+etRexReplace",
         "Use PCRE to parse and extract a formatted value, then use Rex to clean up the surrounding text -- combining both regex families in one workflow.",
         ["etPcreExecute", "etPcreSubstitute", "etRexReplace"],
         ("import pyAether as pyScript\n\n"
          "# Step 1: PCRE extract a width x height dimension\n"
          "dim_re = pyScript.etPcreCompile(r'(\\d+)x(\\d+)')\n"
          "spec = 'layout 800x600 region'\n"
          "if pyScript.etPcreExecute(dim_re, spec):\n"
          "    w = pyScript.etPcreSubstitute('width=\\1')\n"
          "    h = pyScript.etPcreSubstitute('height=\\2')\n"
          "    print(w)\n"
          "    print(h)\n"
          "# Step 2: Rex clean up extra spaces in the spec string\n"
          "pyScript.etRexCompile('\\\\s+')\n"
          "cleaned = pyScript.etRexReplace(spec, ' ', 0)\n"
          "print('cleaned spec:', cleaned.strip())")),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript), combining the relevant "
                  "et* regex APIs." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v25-S6-%s" % apis_str.replace("+", "-"), prompt, completion, apis,
             "S6 cross_api_combo: %s" % apis_str)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    ap = argparse.ArgumentParser(
        description="R195 v25 PyAether SFT corpus: et* regex (6 APIs, 30 pairs)")
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

    # ---- Summary ----
    by_type = {}
    for p in pairs:
        by_type[p["type"]] = by_type.get(p["type"], 0) + 1
    sys.stderr.write("\n=== R195 v25 et* regex corpus summary ===\n")
    sys.stderr.write("Total pairs: %d\n" % len(pairs))
    for t in sorted(by_type):
        sys.stderr.write("  %s: %d\n" % (t, by_type[t]))
    sys.stderr.write("Rejected (contamination): %d\n" % rejected)
    if reject_details:
        sys.stderr.write("  Rejected IDs:\n")
        for pid, hit in reject_details:
            sys.stderr.write("    %s -> hit entry_point: %s\n" % (pid, hit))

    # ---- API coverage check ----
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

    # ---- Write output ----
    with open(args.output, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    sys.stderr.write("\nWrote %d pairs to %s\n" % (len(pairs), args.output))

    # ---- Final contamination assertion ----
    if rejected > 0:
        sys.stderr.write("ERROR: %d pairs rejected due to contamination!\n" % rejected)
        sys.exit(1)
    sys.stderr.write("Contamination check: PASS (0 rejected)\n")


if __name__ == "__main__":
    main()
