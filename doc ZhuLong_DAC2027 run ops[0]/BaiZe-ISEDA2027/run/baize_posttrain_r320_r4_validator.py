#!/usr/bin/env python3
"""
R320: R4 Reward Validator — API Legality Checker for RL GRPO

3-tier API classification (corrects R319's 2-tier wrong/missing):
  - CORRECT: API in expected set for this task
  - VALID_WRONG_CONTEXT: API exists in pyAether DB but not expected for this task
  - HALLUCINATION: API does not exist in pyAether at all
  - MISSING: expected API not used by the model

R4 reward = w1 * (correct / expected_count)
          + w2 * (valid_wrong_context penalty)
          - w3 * (hallucination_count)
          - w4 * (missing_count / expected_count)

The pyAether API DB is loaded from r320_api_db_snapshot.json (offline, no sandbox).
For production RL, augment with pyAether MCP search for unknown APIs.

Zero GPU, zero sandbox — pure offline validation.
"""
import json
import re
import os

RUN_DIR = os.path.dirname(os.path.abspath(__file__))

# == Load API DB snapshot ==
_db_path = os.path.join(RUN_DIR, 'r320_api_db_snapshot.json')
_API_DB = json.load(open(_db_path)) if os.path.exists(_db_path) else {}

# Valid API set: union of expected APIs + MCP-validated valid APIs
VALID_API_SET = set(_API_DB.get('expected_apis', {}).get('sorted_list', []))

# MCP-validated APIs (from R320 MCP search, see r320_mcp_validation.json)
MCP_VALIDATED = {
    # exact_match / high-confidence valid APIs found via MCP search
    'emyDesign', 'emyPoint', 'emyPointF', 'emyPointArrayF', 'emyPointArray',
    'emyInitAether', 'emyTermType', 'emyString', 'emyRect',
    'dbCreateLib', 'dbGetAllLibs', 'dbDelLib', 'dbCloseCV', 'dbNewCV',
    'dbCopyCV', 'dbFindCV', 'emyLib', 'emyLib.create',
    'EmyLPPHeader', 'emyLPPHeader', 'EmyLPPHeader.get',
    'emyRect.all', 'emyRect.net', 'emyPoint.x',
    'emyUInt2String', 'emyStringArray', 'emyArray_emyPoint',
    'buildString', 'QStringList', 'etEvalString',
    'aeDelLib', 'emyBox.init', 'emyTerm.getTermType', 'cdfGet',
    'etClose', 'emyBox',
}
VALID_API_SET.update(MCP_VALIDATED)

# Confirmed hallucinations (MCP search found no match)
CONFIRMED_HALLUCINATIONS = {
    'emyRectF',        # only emyRect exists, no F variant
    'emyCreateLibrary',  # emyLib.create / dbCreateLib exist
    'CellView',        # dbNewCV exists
    'CellView.instances', 'CellView.open',
    'create_cellview', 'create_library',
    'Point',           # generic OOP, not pyAether
    'PointArray',      # generic OOP, not pyAether
    'Polygon', 'polygon',  # generic OOP, not pyAether
    'DM', 'DM.get_view', 'get_view',  # not pyAether
}

# == API extraction from generated code ==
# Pattern: pyAether.XXX, pyScript.XXX, py.XXX, sess.XXX, or bare emy*/db*/sch*/le* calls
_API_PATTERNS = [
    re.compile(r'\bpyAether\.([a-zA-Z_][a-zA-Z0-9_.]*)'),
    re.compile(r'\bpyScript\.([a-zA-Z_][a-zA-Z0-9_.]*)'),
    re.compile(r'\bpy\.([a-zA-Z_][a-zA-Z0-9_.]*)'),
    re.compile(r'\bsess\.([a-zA-Z_][a-zA-Z0-9_.]*)'),
    re.compile(r'\bsession\.([a-zA-Z_][a-zA-Z0-9_.]*)'),
    # Bare pyAether API calls (emy*, db*, sch*, le*, ge*, ae*)
    re.compile(r'\b(emy[A-Z][a-zA-Z0-9_.]*)\b'),
    re.compile(r'\b(db[A-Z][a-zA-Z0-9_.]*)\b'),
    re.compile(r'\b(sch[A-Z][a-zA-Z0-9_.]*)\b'),
    re.compile(r'\b(le[A-Z][a-zA-Z0-9_.]*)\b'),
    re.compile(r'\b(ae[A-Z][a-zA-Z0-9_.]*)\b'),
    re.compile(r'\b(ge[A-Z][a-zA-Z0-9_.]*)\b'),
]

# Exclude Python builtins and common stdlib that match emy*/db* patterns
_EXCLUDE = {
    'emyStr',  # if not a real API
}


def extract_apis(code):
    """Extract pyAether API calls from generated code. Returns set of normalized names."""
    found = set()
    if not code:
        return found
    for pat in _API_PATTERNS:
        for m in pat.finditer(code):
            api = m.group(1) if m.lastindex else m.group(0)
            # Normalize: strip common prefixes
            for pfx in ('pyAether.', 'pyScript.', 'py.', 'sess.', 'session.'):
                if api.startswith(pfx):
                    api = api[len(pfx):]
            if api and api not in _EXCLUDE and len(api) > 2:
                found.add(api)
    return found


def classify_api(api, expected_set):
    """Classify a single API into 3 tiers. Returns category string."""
    if api in expected_set:
        return 'CORRECT'
    if api in CONFIRMED_HALLUCINATIONS:
        return 'HALLUCINATION'
    if api in VALID_API_SET:
        return 'VALID_WRONG_CONTEXT'
    # Unknown — could be hallucination or untested valid API
    # Heuristic: if it starts with a known pyAether prefix, treat as possible valid
    for pfx in ('emy', 'db', 'sch', 'le', 'ae', 'ge', 'Emy', 'CString'):
        if api.startswith(pfx):
            return 'POSSIBLE_VALID_UNKNOWN'
    return 'HALLUCINATION_LIKELY'


def validate_code(code, expected_apis):
    """
    Full validation of generated code against expected APIs.
    Returns dict with classification counts and R4 reward components.
    """
    expected_set = set()
    for a in expected_apis:
        for pfx in ('pyAether.', 'pyScript.', 'py.', 'sess.', 'session.'):
            if a.startswith(pfx):
                a = a[len(pfx):]
        expected_set.add(a)

    found = extract_apis(code)
    classification = {}
    for api in found:
        cat = classify_api(api, expected_set)
        classification[api] = cat

    counts = {'CORRECT': 0, 'VALID_WRONG_CONTEXT': 0, 'HALLUCINATION': 0,
              'POSSIBLE_VALID_UNKNOWN': 0, 'HALLUCINATION_LIKELY': 0}
    for cat in classification.values():
        counts[cat] = counts.get(cat, 0) + 1

    missing = expected_set - found
    n_expected = len(expected_set) if expected_set else 1

    # R4 reward components
    w1 = 1.0   # correct API credit
    w2 = 0.3   # valid wrong context (partial — model knows real API but wrong task)
    w3 = 0.5   # hallucination penalty
    w4 = 0.2   # missing expected API penalty

    r4_reward = (w1 * counts['CORRECT'] / n_expected
                 - w2 * counts['VALID_WRONG_CONTEXT'] / max(len(found), 1)
                 - w3 * counts['HALLUCINATION']
                 - w3 * counts['HALLUCINATION_LIKELY']
                 - w4 * len(missing) / n_expected)
    r4_reward = max(0.0, min(1.0, r4_reward))  # clamp [0, 1]

    return {
        'n_found': len(found),
        'n_expected': len(expected_set),
        'classification': classification,
        'counts': counts,
        'missing': sorted(missing),
        'n_missing': len(missing),
        'r4_reward': round(r4_reward, 4),
        'weights': {'w1': w1, 'w2': w2, 'w3': w3, 'w4': w4},
    }


if __name__ == '__main__':
    # Self-test with sample code
    sample_code = """
import pyAether
def count_unique_bus_bits(bus_string):
    s_name = pyAether.emyString(bus_string)
    num_bits = pyAether.emyStringGetNumUniqueBits(s_name)
    rect = pyAether.emyRectF(0, 0, 100, 100)
    cv = pyAether.CellView("lib", "cell", "view")
    return num_bits
"""
    expected = ['pyAether.emyString', 'pyAether.emyStringGetNumUniqueBits',
                'pyAether.emyNameSpace', 'pyAether.emyCdbaNS']
    result = validate_code(sample_code, expected)
    print('R4 Validator self-test:')
    print(json.dumps(result, indent=2))

