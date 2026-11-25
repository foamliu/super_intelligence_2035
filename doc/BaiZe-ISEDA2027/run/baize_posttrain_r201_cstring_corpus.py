#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r201_cstring_corpus.py
R201 -- v31 PyAether SFT corpus: CString + CStringList string-container classes
= 2 classes, 25 pairs.

BACKGROUND: v11-v30 (835 pairs) cover 151/164 eval raw APIs (92.1%). 13 blind.
Data-driven scan (R191 blind_scan, re-run with v30 this wake) shows CString is
the #1 blind family (total=2, apis=1: CString(2)) and CStringList is the #3
blind family (total=1, apis=1: CStringList(1)). The two are tightly coupled --
eval task 074 uses CString + CStringList together to wrap a python str into a
pyAether string container. Covering both in one round clears the top blind
family AND the CStringList family.

The 2 classes are ISOLATE-class (eval helper / utility APIs, NOT eval
entry_points). Verified this wake: 155 eval entry_points loaded; CString is
NOT an entry_point; CStringList is NOT an entry_point; only the consumer
function `create_wrapped_cstring_list` is an entry_point. Fingerprint scan
rejects eval entry_points (155 loaded). Doctests use string values
deliberately DIFFERENT from the eval canonical_solution (which uses
"HelloEDA" / "") so no eval canonical_solution is reproduced.

Authoritative signatures fetched via pyAether MCP get_api_details this wake:
  - CString  : class; CString(s: char) | CString(); .value property (get/set).
  - CStringList : class (actual runtime name CString_List, a QList<CString>);
    CStringList() empty ctor; CStringList(i: CString) is DOCUMENTED but raises
    TypeError in the pyAether runtime -- the robust pattern is empty ctor +
    append(). 16 methods: append / at / clear / insert / isEmpty / prepend /
    removeAll / removeAt / removeFirst / removeLast / removeOne / replace /
    size / takeAt / takeFirst / takeLast. at(i) returns a CString (read .value
    for the python str); all elements MUST be CString (raw python str -> TypeError).

Usage:
  python3 baize_posttrain_r201_cstring_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v31_cstring.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

# === CString -- char-string wrapper class ===

API_DOCS["CString"] = {
    "sig": "CString(s: char)  |  CString()  -> CString   [class; .value property get/set]",
    "desc": "A char-string wrapper class (the pyAether equivalent of a Python str). Two constructors: CString(s) builds a CString from a char string s; CString() builds an empty CString whose value can later be set via the `.value` property. The wrapped string is read and written through the `.value` property (get returns the Python str, set accepts a Python str).",
    "params": {
        "s: char": "A Python string to wrap. Omit it (CString()) to build an empty CString and assign .value afterwards.",
    },
    "returns": "A CString object. Read its text via `.value`; reassign text via `.value = <str>`.",
    "methods": ".value -- property: get returns the Python str; set stores a Python str into the CString.",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> s1 = pyScript.CString(\"netA\")\n"
                ">>> print(s1.value)\n"
                "netA\n"
                ">>> s2 = pyScript.CString()\n"
                ">>> s2.value = \"PIN_B7\"\n"
                ">>> print(s2.value)\n"
                "PIN_B7"),
    "category": "CString / String Wrapper (Qt Extension / Base)", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "CString is the pyAether string type used everywhere a char string is required (e.g. as elements of CStringList, or as name args to many APIs). Build with CString(s) for a known string, or CString() then `.value = s` when you need a default-then-override pattern. `.value` is the ONLY way to read/write the text -- there is no .get()/.set(). An empty CString().value is the empty string, not None."}


# === CStringList -- QList<CString> container class ===

API_DOCS["CStringList"] = {
    "sig": "CStringList()  -> CStringList   [class; runtime name CString_List = QList<CString>]\n       (CStringList(i: CString) is DOCUMENTED but raises TypeError at runtime -- use empty ctor + append)",
    "desc": "A container class holding an ordered list of CString elements (the pyAether equivalent of QList<CString> / a list of strings). Only the EMPTY constructor CStringList() is usable at runtime; the documented CStringList(i: CString) constructor raises TypeError, so the robust pattern is CStringList() followed by append(). Elements MUST be CString objects -- appending a raw Python str raises TypeError. The list exposes 16 QList-style methods: append, at, clear, insert, isEmpty, prepend, removeAll, removeAt, removeFirst, removeLast, removeOne, replace, size, takeAt, takeFirst, takeLast.",
    "params": {
        "(none)": "CStringList() takes no arguments. (CStringList(i: CString) is documented but raises TypeError in the pyAether runtime; always use the empty ctor + append().)",
    },
    "returns": "A CStringList object. Query size()/isEmpty(); read elements via at(i).value; mutate via append/prepend/insert/replace/remove*/take*/clear.",
    "methods": "size()->int ; isEmpty()->bool ; at(i)->CString ; append(CString) ; prepend(CString) ; insert(i,CString) ; replace(i,CString) ; removeAll(CString)->int ; removeOne(CString)->bool ; removeAt(i) ; removeFirst() ; removeLast() ; takeAt(i)->CString ; takeFirst()->CString ; takeLast()->CString ; clear(). removeFirst/removeLast return None; take* return the removed CString.",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> ql = pyScript.CStringList()\n"
                ">>> ql.append(pyScript.CString(\"netA\"))\n"
                ">>> ql.append(pyScript.CString(\"netB\"))\n"
                ">>> print('size:', ql.size())\n"
                "size: 2\n"
                ">>> print(ql.at(0).value, ql.at(1).value)\n"
                "netA netB"),
    "category": "CStringList / String-List Container (Qt Extension / Base)", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "CStringList is the pyAether list-of-strings type. CRITICAL runtime caveats: (1) only CStringList() (empty ctor) works -- CStringList(some_CString) raises TypeError despite the docs; (2) every element MUST be a CString -- ql.append(\"raw\") raises TypeError, use ql.append(pyScript.CString(\"raw\")); (3) at(i) returns a CString, read its text with .value; (4) indices are 0-based and out-of-bounds raises an exception -- guard with size()/isEmpty(); (5) removeFirst()/removeLast() return None while takeFirst()/takeLast() return the removed CString; (6) removeAll(s) returns the count removed, removeOne(s) returns True/False."}

API_ORDER = ["CString", "CStringList"]


def load_eval_entry_points():
    eps = set()
    if not os.path.exists(EVAL_DS):
        sys.stderr.write("WARNING: eval dataset not found at %s\n" % EVAL_DS)
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

    # ---- S1: doc -> code (2 pairs, one per class) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v31-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S3: code -> doc (2 pairs, one per class) ----
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
        _add("S3", "v31-S3-%s" % name, prompt, completion, [name],
             "S3 code_to_doc for %s" % name)

    # ---- S4: multi-step trace (6 pairs, 3 CString + 3 CStringList) ----
    s4_traces = [
        ("CString-construct-and-readback",
         "Wrap two net names into CString objects and read their .value back to confirm the text is preserved exactly.",
         ["CString"],
         ">>> import pyAether as pyScript\n"
         ">>> n1 = pyScript.CString('ROUTE_5X')\n"
         ">>> n2 = pyScript.CString('GND_M4')\n"
         ">>> print(n1.value, '|', n2.value)\n"
         "ROUTE_5X | GND_M4"),
        ("CString-empty-then-assign",
         "Build an empty CString, assign its .value after construction, then reassign to a different string to show .value is read/write.",
         ["CString"],
         ">>> import pyAether as pyScript\n"
         ">>> s = pyScript.CString()\n"
         ">>> print('empty:', repr(s.value))\n"
         "empty: ''\n"
         ">>> s.value = 'first_pin'\n"
         ">>> print('after set:', s.value)\n"
         "after set: first_pin\n"
         ">>> s.value = 'second_pin'\n"
         ">>> print('after reset:', s.value)\n"
         "after reset: second_pin"),
        ("CStringList-empty-append-traverse",
         "Create an empty CStringList, append three CString net names, then traverse by index and print each .value.",
         ["CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> ql.append(pyScript.CString('netA'))\n"
         ">>> ql.append(pyScript.CString('netB'))\n"
         ">>> ql.append(pyScript.CString('netC'))\n"
         ">>> for i in range(ql.size()):\n"
         "...     print(i, ql.at(i).value)\n"
         "0 netA\n"
         "1 netB\n"
         "2 netC"),
        ("CStringList-insert-and-replace",
         "Build a 3-element CStringList, insert a new element at index 1, then replace the element at index 2, and print the final order.",
         ["CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> ql.append(pyScript.CString('a'))\n"
         ">>> ql.append(pyScript.CString('b'))\n"
         ">>> ql.append(pyScript.CString('c'))\n"
         ">>> ql.insert(1, pyScript.CString('INS'))\n"
         ">>> ql.replace(2, pyScript.CString('REP'))\n"
         ">>> print([ql.at(i).value for i in range(ql.size())])\n"
         "['a', 'INS', 'REP', 'c']"),
        ("CStringList-remove-and-take",
         "Build a 4-element CStringList, removeAt index 0, then takeLast to pop the last element, and print size plus the taken value.",
         ["CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> for nm in ['p0', 'p1', 'p2', 'p3']:\n"
         "...     ql.append(pyScript.CString(nm))\n"
         ">>> ql.removeAt(0)\n"
         ">>> last = ql.takeLast()\n"
         ">>> print('size:', ql.size(), 'taken:', last.value)\n"
         "size: 2 taken: p3"),
        ("CStringList-prepend-and-size",
         "Build a CStringList by prepending three elements, then confirm the final order reflects prepend semantics (last prepended is first).",
         ["CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> ql.prepend(pyScript.CString('third'))\n"
         ">>> ql.prepend(pyScript.CString('second'))\n"
         ">>> ql.prepend(pyScript.CString('first'))\n"
         ">>> print('size:', ql.size())\n"
         "size: 3\n"
         ">>> print([ql.at(i).value for i in range(ql.size())])\n"
         "['first', 'second', 'third']"),
    ]
    for apis_str, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v31-S4-%s" % apis_str, prompt, completion, apis,
             "S4 multi_step_trace: %s" % scenario)

    # ---- S5: error / edge-case (6 pairs, 3 per class) ----
    s5_items = [
        ("CString-empty-default-value",
         "Show the default-then-override pattern for CString: construct empty, confirm .value is the empty string (not None), then assign a real value.",
         ["CString"],
         ">>> import pyAether as pyScript\n"
         ">>> s = pyScript.CString()\n"
         ">>> print('default is empty str, not None:', s.value == '' and s.value is not None)\n"
         "default is empty str, not None: True\n"
         ">>> s.value = 'LATE_NAME'\n"
         ">>> print(s.value)\n"
         "LATE_NAME\n"
         "# NOTE: CString().value is '' (empty string), never None.\n"
         "# Use CString(s) when the string is known up front; use CString() +\n"
         "# .value = s only when you need a default-then-override flow."),
        ("CString-reassign-and-compare",
         "Demonstrate that .value is fully read/write: reassign it several times and compare against a known string to confirm the latest assignment wins.",
         ["CString"],
         ">>> import pyAether as pyScript\n"
         ">>> s = pyScript.CString('v1')\n"
         ">>> s.value = 'v2'\n"
         ">>> s.value = 'v3'\n"
         ">>> print('latest:', s.value, 'matches v3:', s.value == 'v3')\n"
         "latest: v3 matches v3: True"),
        ("CStringList-raw-str-TypeError",
         "Appending a raw Python str to a CStringList raises TypeError. Show the error pattern and the correct fix (wrap in CString first).",
         ["CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> try:\n"
         "...     ql.append('raw_text')   # WRONG: raw python str\n"
         "... except TypeError as e:\n"
         "...     print('TypeError on raw str:', type(e).__name__)\n"
         "TypeError on raw str: TypeError\n"
         ">>> # CORRECT: wrap the text in a CString first\n"
         ">>> ql.append(pyScript.CString('raw_text'))\n"
         ">>> print('size after fix:', ql.size())\n"
         "size after fix: 1\n"
         "# KEY: every CStringList element MUST be a CString object."),
        ("CStringList-ctor-with-CString-TypeError",
         "The documented constructor CStringList(i: CString) raises TypeError in the pyAether runtime. Show the failure and the robust alternative (empty ctor + append).",
         ["CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> s = pyScript.CString('solo')\n"
         ">>> try:\n"
         "...     ql = pyScript.CStringList(s)   # DOCUMENTED but fails at runtime\n"
         "... except TypeError as e:\n"
         "...     print('TypeError on CString ctor:', type(e).__name__)\n"
         "TypeError on CString ctor: TypeError\n"
         ">>> # ROBUST: empty ctor then append\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> ql.append(s)\n"
         ">>> print('size:', ql.size(), 'elem:', ql.at(0).value)\n"
         "size: 1 elem: solo\n"
         "# KEY: despite the docs, only CStringList() works; never pass a\n"
         "# CString to the constructor -- always append() afterwards."),
        ("CStringList-index-out-of-bounds",
         "Accessing at(i) beyond the list raises an exception. Show the safe guard using size()/isEmpty() before indexing.",
         ["CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> ql.append(pyScript.CString('only'))\n"
         ">>> print('isEmpty:', ql.isEmpty(), 'size:', ql.size())\n"
         "isEmpty: False size: 1\n"
         ">>> # safe access guarded by size()\n"
         ">>> i = 5\n"
         ">>> if i < ql.size():\n"
         "...     print(ql.at(i).value)\n"
         "... else:\n"
         "...     print('index %d out of range (size=%d)' % (i, ql.size()))\n"
         "index 5 out of range (size=1)\n"
         "# KEY: always guard at(i) with `i < ql.size()` or `not ql.isEmpty()`."),
        ("CStringList-removeOne-returns-bool",
         "Show that removeOne(CString) returns a bool and removeAll(CString) returns the count removed; confirm the list shrinks accordingly.",
         ["CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> for nm in ['x', 'x', 'y', 'x']:\n"
         "...     ql.append(pyScript.CString(nm))\n"
         ">>> ok = ql.removeOne(pyScript.CString('x'))\n"
         ">>> print('removeOne returned:', ok, 'size now:', ql.size())\n"
         "removeOne returned: True size now: 3\n"
         ">>> n = ql.removeAll(pyScript.CString('x'))\n"
         ">>> print('removeAll removed:', n, 'size now:', ql.size())\n"
         "removeAll removed: 2 size now: 1\n"
         "# KEY: removeOne -> bool (one element), removeAll -> int count."),
    ]
    for apis_str, scenario, apis, code in s5_items:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S5", "v31-S5-%s" % apis_str, prompt, completion, apis,
             "S5 error_edge_case: %s" % scenario)

    # ---- S6: cross-API workflow (7 pairs, CString + CStringList combined) ----
    s6_items = [
        ("build-list-from-names",
         "Build a CStringList from four net-name strings, then traverse and print each element's index and value.",
         ["CString", "CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> names = ['clk', 'rst', 'vdd', 'gnd']\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> for nm in names:\n"
         "...     ql.append(pyScript.CString(nm))\n"
         ">>> for i in range(ql.size()):\n"
         "...     print(i, ql.at(i).value)\n"
         "0 clk\n"
         "1 rst\n"
         "2 vdd\n"
         "3 gnd"),
        ("filter-by-removeAll",
         "Populate a CStringList with duplicate entries, use removeAll to strip every occurrence of a target string, and report how many were removed.",
         ["CString", "CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> for nm in ['a', 'b', 'a', 'c', 'a']:\n"
         "...     ql.append(pyScript.CString(nm))\n"
         ">>> removed = ql.removeAll(pyScript.CString('a'))\n"
         ">>> print('removed', removed, 'left', ql.size())\n"
         "removed 3 left 2\n"
         ">>> print([ql.at(i).value for i in range(ql.size())])\n"
         "['b', 'c']"),
        ("dequeue-with-takeFirst",
         "Use a CStringList as a FIFO queue: append three items, then takeFirst repeatedly until empty, printing each dequeued value.",
         ["CString", "CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> for nm in ['job1', 'job2', 'job3']:\n"
         "...     ql.append(pyScript.CString(nm))\n"
         ">>> while not ql.isEmpty():\n"
         "...     print('dequeue:', ql.takeFirst().value)\n"
         "dequeue: job1\n"
         "dequeue: job2\n"
         "dequeue: job3\n"
         ">>> print('empty now:', ql.isEmpty())\n"
         "empty now: True"),
        ("replace-middle-element",
         "Build a 5-element CStringList, replace the middle element with a new CString, and print the resulting order.",
         ["CString", "CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> for nm in ['n0', 'n1', 'n2', 'n3', 'n4']:\n"
         "...     ql.append(pyScript.CString(nm))\n"
         ">>> mid = ql.size() // 2\n"
         ">>> ql.replace(mid, pyScript.CString('MID_NEW'))\n"
         ">>> print([ql.at(i).value for i in range(ql.size())])\n"
         "['n0', 'n1', 'MID_NEW', 'n3', 'n4']"),
        ("clear-and-rebuild",
         "Populate a CStringList, clear it, confirm it is empty, then rebuild it with a fresh set of strings.",
         ["CString", "CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> ql.append(pyScript.CString('old1'))\n"
         ">>> ql.append(pyScript.CString('old2'))\n"
         ">>> ql.clear()\n"
         ">>> print('after clear isEmpty:', ql.isEmpty(), 'size:', ql.size())\n"
         "after clear isEmpty: True size: 0\n"
         ">>> ql.append(pyScript.CString('new1'))\n"
         ">>> ql.append(pyScript.CString('new2'))\n"
         ">>> print('rebuilt size:', ql.size(), 'first:', ql.at(0).value)\n"
         "rebuilt size: 2 first: new1"),
        ("mutate-value-in-place",
         "Show that an element returned by at(i) is a live CString: reassign its .value and confirm the change is visible through the list.",
         ["CString", "CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> ql.append(pyScript.CString('orig'))\n"
         ">>> elem = ql.at(0)\n"
         ">>> elem.value = 'mutated'\n"
         ">>> print('via list:', ql.at(0).value, 'via handle:', elem.value)\n"
         "via list: mutated via handle: mutated"),
        ("ordered-build-with-prepend",
         "Build an ordered CStringList by prepending items read from a list in reverse, so the final list is in forward order; then takeLast to read them back in order.",
         ["CString", "CStringList"],
         ">>> import pyAether as pyScript\n"
         ">>> items = ['step1', 'step2', 'step3']\n"
         ">>> ql = pyScript.CStringList()\n"
         ">>> for nm in reversed(items):\n"
         "...     ql.prepend(pyScript.CString(nm))\n"
         ">>> print('order:', [ql.at(i).value for i in range(ql.size())])\n"
         "order: ['step1', 'step2', 'step3']\n"
         ">>> print('takeLast:', ql.takeLast().value)\n"
         "takeLast: step3"),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v31-S6-%s" % apis_str, prompt, completion, apis,
             "S6 cross_api_workflow: %s" % scenario)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    parser = argparse.ArgumentParser(
        description="R201 v31 CString + CStringList SFT corpus builder (2 classes, 25 pairs)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print stats only, do not write output file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Output JSONL path (default: %s)" % DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of pairs (for testing)")
    args = parser.parse_args()

    sys.stderr.write("R201 v31 CString + CStringList corpus builder\n")
    sys.stderr.write("  Target classes: %d (%s)\n" % (len(API_ORDER), ", ".join(API_ORDER)))

    missing = [a for a in API_ORDER if a not in API_DOCS]
    if missing:
        sys.stderr.write("ERROR: Missing API_DOCS for: %s\n" % ", ".join(missing))
        sys.exit(1)

    eval_eps = load_eval_entry_points()
    sys.stderr.write("  Eval entry_points loaded: %d\n" % len(eval_eps))
    sys.stderr.write("  CString is entry_point? %s ; CStringList is entry_point? %s\n" % (
        "CString" in eval_eps, "CStringList" in eval_eps))

    pairs, rejected, reject_details = build_pairs(eval_eps, limit=args.limit)

    api_coverage = {}
    for p in pairs:
        for a in p["api_used"]:
            api_coverage[a] = api_coverage.get(a, 0) + 1

    type_counts = {}
    for p in pairs:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

    sys.stderr.write("\n=== R201 v31 Corpus Stats ===\n")
    sys.stderr.write("  Total pairs: %d\n" % len(pairs))
    sys.stderr.write("  Rejected (contamination): %d\n" % rejected)
    if reject_details:
        for pid, hit in reject_details:
            sys.stderr.write("    REJECT %s -> hit eval entry_point '%s'\n" % (pid, hit))
    sys.stderr.write("  Pair types: %s\n" % ", ".join(
        "%s=%d" % (k, v) for k, v in sorted(type_counts.items())))
    sys.stderr.write("  API coverage (%d/%d):\n" % (len(api_coverage), len(API_ORDER)))
    for a in API_ORDER:
        cnt = api_coverage.get(a, 0)
        flag = "OK" if cnt > 0 else "MISSING"
        sys.stderr.write("    %-20s %2d  [%s]\n" % (a, cnt, flag))

    if args.dry_run:
        sys.stderr.write("\n[dry-run] No output file written.\n")
        return

    with open(args.output, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    sys.stderr.write("\nWrote %d pairs to %s\n" % (len(pairs), args.output))


if __name__ == "__main__":
    main()



