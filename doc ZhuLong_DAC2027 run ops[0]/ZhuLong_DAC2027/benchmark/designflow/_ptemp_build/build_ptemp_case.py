#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builder for EDA-Eval-DesignFlow-PtempCondUsageAnalyze-001 (shard A, r646).
C-A analysis-Q&A: trace where ptemp is used as a decision criterion in a SPICE sim setup.
Generates check.py (self-contained, A_FILES+B_SPEC base64-inlined), reference submit,
5 negatives + 3 fakes + negative_selftest, and the jsonl entry. Packs into case.tar.gz.
Run on .75 where clean A files live.
"""
import base64, json, os, re, zipfile, io, hashlib, tarfile, subprocess, sys, inspect

WORK = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/_ptemp_build"
CASE_ID = "EDA-Eval-DesignFlow-PtempCondUsageAnalyze-001"
DOMAIN = "eda_other"
TRACE = {
    "user": "ghyang", "host": "10.129.8.225", "host_ip": "10.129.8.225",
    "session_file": "1793084065593_fg1kv.messages.json",
    "match_count": 33,
    "real_task_summary": "FineSim/SPICE 仿真配置分析：sim_p1_pl3.sp 中定义的温度参数 ptemp 在哪里被作为判断依据起作用（追踪 ptemp 经 .inc 包含的 Pattern_Power_CRG.sp 中 .if/.elseif/.else 条件块选择温度相关的偏置电压）",
}

# ---- Load clean A files (line numbers already stripped) ----
sim_a = open(WORK + "/fg1kv/clean_sim_p1_pl3.sp").read()
pow_a = open(WORK + "/fg1kv/clean_Pattern_Power_CRG.sp").read()
A_FILES = {"sim_p1_pl3.sp": sim_a, "Pattern_Power_CRG.sp": pow_a}

# ---- B variant (hidden, synthetic but realistic, all 9 anti-hardcode dims differ from A) ----
B_MANUAL = """# B variant — drgsa_b DDR5 project, sim_b3_pl2.sp
# Project path: /proj/drgsa_b/V0/workdir/ghyang/sim_b3_pl2.sp
# Temperature parameter: .param ptemp =125
# Simulator temperature directive: .temp 125c
# Power table include: .inc "/proj/drgsa_b/V0/workdir/ytzhu/simulation/setup/Pattern_Power_DDR.sp"
#
# Pattern_Power_DDR.sp structure:
#   5 pvcc bands: 0.95-1.0, 1.0-1.05, 1.05-1.1, 1.1-1.2, 1.2-1.3
#   each band has nested .if (ptemp==125) / .elseif (ptemp==-25) / .else / .endif
# Controlled params (temperature-dependent): pvwl, pvbl, pvblbk, pvmwl, pvso
# Cold branch (ptemp==125): pvwl=3.0v, pvso=1.5v
# Hot branch (ptemp==-25): pvwl=2.7v, pvso=1.38v
"""
B_SPEC = {"project_name": "drgsa_b", "manual_text": B_MANUAL}

# ---- _parse_a: extract A-truth (8 verifiable dims; project_name is 9th, skipped in A-match) ----
def _parse_a(files):
    sim = files.get("sim_p1_pl3.sp", "")
    powt = files.get("Pattern_Power_CRG.sp", "")
    def _s(pat, text, default=""):
        m = re.search(pat, text, re.S)
        return m.group(1) if m else default
    project_name = _s(r"/proj/(\w+)/", sim, "")
    ptemp_value = _s(r"\.param\s+ptemp\s*=\s*(-?\d+)", sim, "")
    temp_directive = _s(r"\.temp\s+(-?\d+c?)", sim, "")
    power_table_file = _s(r"(\w*Pattern_Power\w*\.sp)", sim, "")
    pvcc_band_count = len(re.findall(r"\.if\s+\(ptemp==", powt))
    branches = re.findall(r"ptemp==(-?\d+)", powt)
    seen = []
    for b in branches:
        if b not in seen:
            seen.append(b)
    ptemp_branch_values = seen
    cps = re.findall(r"\.param\s+(pvwlp|pvblh|pvblhbk|pvmwln|pviso)\b", powt)
    controlled_params = []
    for c in cps:
        if c not in controlled_params:
            controlled_params.append(c)
    cold_pvwl_value = _s(r"\.if\s+\(ptemp==-40\).*?\.param\s+pvwlp\s*=\s*([0-9.]+v)", powt, "")
    hot_pviso_value = _s(r"\.elseif\s+\(ptemp==98\).*?\.param\s+pviso\s*=\s*([0-9.]+v)", powt, "")
    return {
        "project_name": project_name,
        "ptemp_value": ptemp_value,
        "temp_directive": temp_directive,
        "power_table_file": power_table_file,
        "pvcc_band_count": pvcc_band_count,
        "ptemp_branch_values": ptemp_branch_values,
        "controlled_params": controlled_params,
        "cold_pvwl_value": cold_pvwl_value,
        "hot_pviso_value": hot_pviso_value,
    }

# ---- _parse_b: extract B-truth from manual_text ----
def _parse_b(spec):
    text = spec.get("manual_text", "")
    def _s(pat, default=""):
        m = re.search(pat, text, re.S)
        return m.group(1) if m else default
    project_name = _s(r"/proj/(\w+)/", "")
    ptemp_value = _s(r"\.param\s+ptemp\s*=\s*(-?\d+)", "")
    temp_directive = _s(r"\.temp\s+(-?\d+c?)", "")
    power_table_file = _s(r"(\w*Pattern_Power\w*\.sp)", "")
    n = _s(r"(\d+)\s*pvcc bands", "")
    pvcc_band_count = int(n) if n.isdigit() else 0
    m = re.search(r"\.if\s+\(ptemp==(-?\d+)\)\s*/\s*\.elseif\s+\(ptemp==(-?\d+)\)", text)
    ptemp_branch_values = [m.group(1), m.group(2)] if m else []
    cps = _s(r"Controlled params[^:]*:\s*([\w, ]+)", "")
    controlled_params = [c.strip() for c in cps.split(",") if c.strip()] if cps else []
    cold_pvwl_value = _s(r"Cold[^:]*:\s*pvwl=([0-9.]+v)", "")
    hot_pviso_value = _s(r"Hot[^:]*:.*?pvso=([0-9.]+v)", "")
    return {
        "project_name": project_name,
        "ptemp_value": ptemp_value,
        "temp_directive": temp_directive,
        "power_table_file": power_table_file,
        "pvcc_band_count": pvcc_band_count,
        "ptemp_branch_values": ptemp_branch_values,
        "controlled_params": controlled_params,
        "cold_pvwl_value": cold_pvwl_value,
        "hot_pviso_value": hot_pviso_value,
    }

A_EXP = _parse_a(A_FILES)
B_EXP = _parse_b(B_SPEC)
ANTI_DIMS = ["project_name","ptemp_value","temp_directive","power_table_file",
             "pvcc_band_count","ptemp_branch_values","controlled_params",
             "cold_pvwl_value","hot_pviso_value"]

diffs = sum(1 for d in ANTI_DIMS if A_EXP[d] != B_EXP[d])
assert diffs >= 6, "A/B differ on only %d/9 dims" % diffs
for d in ANTI_DIMS:
    assert A_EXP[d] not in ("", [], 0, None), "A_EXP[%s] empty: %r" % (d, A_EXP[d])

print("A_EXP:", json.dumps(A_EXP, ensure_ascii=False))
print("B_EXP:", json.dumps(B_EXP, ensure_ascii=False))
print("A/B diffs: %d/9" % diffs)

# ===================== build check.py =====================
A_B64 = base64.b64encode(json.dumps(A_FILES, ensure_ascii=False).encode("utf-8")).decode("ascii")
B_B64 = base64.b64encode(json.dumps(B_SPEC, ensure_ascii=False).encode("utf-8")).decode("ascii")

CHECK_PY = '#!/usr/bin/env python3\n'
CHECK_PY += '"""check.py for %s — ptemp conditional usage analysis (C-A analysis-Q&A).\n' % CASE_ID
CHECK_PY += 'Self-contained: A_FILES + B_SPEC base64-inlined. Run: python3 check.py <deliverable.zip> <workdir>.\n"""\n'
CHECK_PY += 'import base64, json, re, zipfile, os, random, hashlib, sys\n\n'
CHECK_PY += 'A_FILES = json.loads(base64.b64decode("' + A_B64 + '").decode("utf-8"))\n'
CHECK_PY += 'B_SPEC = json.loads(base64.b64decode("' + B_B64 + '").decode("utf-8"))\n\n'
CHECK_PY += inspect.getsource(_parse_b) + "\n"
CHECK_PY += 'B_EXP = _parse_b(B_SPEC)\n'
CHECK_PY += inspect.getsource(_parse_a) + "\n"
CHECK_PY += 'A_EXP = _parse_a(A_FILES)\n'
CHECK_PY += 'ANTI_DIMS = ' + repr(ANTI_DIMS) + '\n'
CHECK_PY += '''
REQUIRED_SECTIONS = ["report_overview","ptemp_definition","include_chain",
    "conditional_structure","temperature_values","controlled_parameters",
    "mechanism","ptemp_facts","evidence","conclusion"]

def _load_report(deliverable):
    if not os.path.exists(deliverable):
        raise AssertionError("deliverable not found: %s" % deliverable)
    try:
        z = zipfile.ZipFile(deliverable)
    except Exception as e:
        raise AssertionError("not a valid zip: %s" % e)
    names = z.namelist()
    target = "ptemp_usage_analysis_report.json"
    if target not in names:
        raise AssertionError("zip missing %s; got %s" % (target, names))
    raw = z.read(target)
    try:
        rep = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise AssertionError("report not valid JSON: %s" % e)
    if not isinstance(rep, dict):
        raise AssertionError("report not a JSON object")
    return rep

CONDS = []
def cond(label, desc):
    def deco(fn):
        CONDS.append((label, desc, fn))
        return fn
    return deco
'''

CHECK_PY += '''
@cond("a","submit.zip exists, valid zip, contains ptemp_usage_analysis_report.json as valid JSON object")
def _a(deliverable, workdir):
    _load_report(deliverable)

@cond("b","report has >=8 required top-level sections")
def _b(deliverable, workdir):
    rep = _load_report(deliverable)
    missing = [s for s in REQUIRED_SECTIONS if s not in rep]
    if len(missing) > 2:
        raise AssertionError("missing %d required sections: %s" % (len(missing), missing))

@cond("c","ptemp_definition: file=sim_p1_pl3.sp, param_name=ptemp, value=-40")
def _c(deliverable, workdir):
    rep = _load_report(deliverable)
    pd = rep.get("ptemp_definition", {})
    if not isinstance(pd, dict) or not pd:
        raise AssertionError("ptemp_definition missing/empty")
    if str(pd.get("file","")) != "sim_p1_pl3.sp":
        raise AssertionError("ptemp_definition.file got %r want sim_p1_pl3.sp" % pd.get("file"))
    if str(pd.get("param_name","")).lower() != "ptemp":
        raise AssertionError("ptemp_definition.param_name got %r want ptemp" % pd.get("param_name"))
    if str(pd.get("value","")) != "-40":
        raise AssertionError("ptemp_definition.value got %r want -40" % pd.get("value"))

@cond("d","ptemp_definition identifies .param ptemp=-40 at line 15 of sim_p1_pl3.sp")
def _d(deliverable, workdir):
    rep = _load_report(deliverable)
    pd = rep.get("ptemp_definition", {})
    line = pd.get("line","")
    if str(line).strip() != "15":
        raise AssertionError("ptemp_definition.line got %r want 15" % line)

@cond("e","include_chain: Pattern_Power_CRG.sp included via .inc from sim_p1_pl3.sp")
def _e(deliverable, workdir):
    rep = _load_report(deliverable)
    ic = rep.get("include_chain", {})
    if not isinstance(ic, dict) or not ic:
        raise AssertionError("include_chain missing/empty")
    inc_file = str(ic.get("included_file",""))
    if "Pattern_Power_CRG.sp" not in inc_file:
        raise AssertionError("include_chain.included_file got %r want Pattern_Power_CRG.sp" % inc_file)
    if str(ic.get("sim_file","")) != "sim_p1_pl3.sp":
        raise AssertionError("include_chain.sim_file got %r want sim_p1_pl3.sp" % ic.get("sim_file"))

@cond("f","conditional_structure: outer var=pvcc, inner var=ptemp, 2-level nesting described")
def _f(deliverable, workdir):
    rep = _load_report(deliverable)
    cs = rep.get("conditional_structure", {})
    if not isinstance(cs, dict) or not cs:
        raise AssertionError("conditional_structure missing/empty")
    blob = json.dumps(cs, ensure_ascii=False).lower()
    if "pvcc" not in blob:
        raise AssertionError("conditional_structure missing pvcc (outer var)")
    if "ptemp" not in blob:
        raise AssertionError("conditional_structure missing ptemp (inner var)")
    if "if" not in blob and "cond" not in blob:
        raise AssertionError("conditional_structure missing conditional (.if) reference")

@cond("g","conditional_structure: outer_bands_count >= 6 (actual 7 bands with ptemp)")
def _g(deliverable, workdir):
    rep = _load_report(deliverable)
    cs = rep.get("conditional_structure", {})
    n = cs.get("outer_bands_count", cs.get("pvcc_band_count", 0))
    try:
        n = int(n)
    except Exception:
        n = 0
    if n < 6:
        raise AssertionError("outer_bands_count got %r want >=6" % cs.get("outer_bands_count"))

@cond("h","temperature_values: branch values include -40 and 98 (+ else)")
def _h(deliverable, workdir):
    rep = _load_report(deliverable)
    tv = rep.get("temperature_values", {})
    blob = json.dumps(tv, ensure_ascii=False)
    if "-40" not in blob:
        raise AssertionError("temperature_values missing -40")
    if "98" not in blob:
        raise AssertionError("temperature_values missing 98")

@cond("i","controlled_parameters: includes >=4 of {pvwlp,pvblh,pvblhbk,pvmwln,pviso}")
def _i(deliverable, workdir):
    rep = _load_report(deliverable)
    cp = rep.get("controlled_parameters", {})
    blob = json.dumps(cp, ensure_ascii=False).lower()
    expected = ["pvwlp","pvblh","pvblhbk","pvmwln","pviso"]
    hits = sum(1 for p in expected if p in blob)
    if hits < 4:
        raise AssertionError("controlled_parameters matched only %d/5 expected params" % hits)

@cond("j","controlled_parameters: cold (ptemp==-40) vs hot (ptemp==98) values differ")
def _j(deliverable, workdir):
    rep = _load_report(deliverable)
    cp = rep.get("controlled_parameters", {})
    blob = json.dumps(cp, ensure_ascii=False)
    cold_hot = (("2.8" in blob and "2.6" in blob) or ("1.44" in blob and "1.36" in blob))
    if not cold_hot:
        raise AssertionError("controlled_parameters does not show cold-vs-hot value difference")

@cond("k","mechanism: ptemp acts as decision criterion selecting temperature-dependent bias voltages")
def _k(deliverable, workdir):
    rep = _load_report(deliverable)
    me = rep.get("mechanism", {})
    blob = json.dumps(me, ensure_ascii=False).lower()
    if "ptemp" not in blob:
        raise AssertionError("mechanism missing ptemp")
    if "decision" not in blob and "select" not in blob and "judg" not in blob and "condition" not in blob:
        raise AssertionError("mechanism missing decision/select/condition keyword")
    if "volt" not in blob and "bias" not in blob:
        raise AssertionError("mechanism missing voltage/bias keyword")

@cond("l","evidence: >=4 entries, each source_file in A files, token is real substring of that A file")
def _l(deliverable, workdir):
    rep = _load_report(deliverable)
    ev = rep.get("evidence", [])
    if not isinstance(ev, list) or len(ev) < 4:
        raise AssertionError("evidence has %d entries, want >=4" % (len(ev) if isinstance(ev,list) else 0))
    valid = 0
    for e in ev:
        if not isinstance(e, dict):
            continue
        sf = str(e.get("source_file",""))
        tok = str(e.get("token",""))
        if sf in A_FILES and tok and tok in A_FILES[sf]:
            valid += 1
    if valid < 4:
        raise AssertionError("only %d/%d evidence entries have valid (source_file in A, token=real substring)" % (valid, len(ev)))

@cond("m","ptemp_facts: all 9 anti-hardcode dims populated")
def _m(deliverable, workdir):
    rep = _load_report(deliverable)
    ff = rep.get("ptemp_facts", {})
    if not isinstance(ff, dict):
        raise AssertionError("ptemp_facts not an object")
    for dim in ANTI_DIMS:
        v = ff.get(dim)
        if v in (None, "", [], 0) or (isinstance(v, str) and not v.strip()):
            raise AssertionError("ptemp_facts.%s missing/empty" % dim)

@cond("n","B judge-self-check: ptemp_facts match A-truth on >=6/8 dims AND differ from B-truth on >=6/9 dims")
def _n(deliverable, workdir):
    rep = _load_report(deliverable)
    ff = rep.get("ptemp_facts", {})
    a_match = 0
    a_mm = []
    for dim in ANTI_DIMS:
        if dim == "project_name":
            continue
        if ff.get(dim) == A_EXP.get(dim):
            a_match += 1
        else:
            a_mm.append(dim)
    if a_match < 6:
        raise AssertionError("ptemp_facts matches A-truth on only %d/8 dims; mismatch: %s" % (a_match, a_mm))
    b_diff = 0
    b_dn = []
    for dim in ANTI_DIMS:
        if ff.get(dim) != B_EXP[dim]:
            b_diff += 1
            b_dn.append(dim)
    if b_diff < 6:
        raise AssertionError("report matches B truth on too many dims (%d differ; need >=6). Diff: %s" % (b_diff, b_dn))

@cond("o","3-seed determinism: shuffle B_SPEC manual_text 3x; _parse_b order-independent; B truth sha256 stable")
def _o(deliverable, workdir):
    base = B_SPEC.get("manual_text","").split("\\n")
    hashes = set()
    for seed in (1,2,3):
        rnd = random.Random(seed)
        lines = list(base)
        rnd.shuffle(lines)
        spec = dict(B_SPEC)
        spec["manual_text"] = "\\n".join(lines)
        truth = _parse_b(spec)
        h = hashlib.sha256(json.dumps(truth, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        hashes.add(h)
        if truth["ptemp_value"] != "125":
            raise AssertionError("seed %d: parser lost ptemp_value (got %r)" % (seed, truth["ptemp_value"]))
        if truth["power_table_file"] != "Pattern_Power_DDR.sp":
            raise AssertionError("seed %d: parser lost power_table_file (got %r)" % (seed, truth["power_table_file"]))
    if len(hashes) != 1:
        raise AssertionError("B truth not stable across 3 seeds (%d distinct hashes)" % len(hashes))

@cond("p","conclusion.verdict non-empty AND confidence in {high,medium,low} AND methodology non-empty")
def _p(deliverable, workdir):
    rep = _load_report(deliverable)
    cv = rep.get("conclusion", {}).get("verdict")
    if not isinstance(cv, str) or not cv.strip():
        raise AssertionError("conclusion.verdict missing/empty")
    conf = str(rep.get("confidence","")).strip().lower()
    if conf not in ("high","medium","low"):
        raise AssertionError("confidence got %r want high/medium/low" % conf)
    meth = str(rep.get("methodology",""))
    if not meth.strip():
        raise AssertionError("methodology missing/empty")

def check(deliverable, workdir):
    results = []
    first_fail = None
    for label, desc, fn in CONDS:
        try:
            fn(deliverable, workdir)
            results.append((label, desc, "PASS"))
        except Exception as e:
            results.append((label, desc, "FAIL: %s" % e))
            first_fail = (label, desc, str(e))
            break
    for label, desc, status in results:
        print("[%s] %s : %s" % (label, desc, status))
    if first_fail is None:
        print("ALL PASS (%d/%d)" % (len(CONDS), len(CONDS)))
        return True
    print("FAIL at condition %s: %s" % (first_fail[0], first_fail[2]))
    raise AssertionError("check failed at %s: %s" % (first_fail[0], first_fail[2]))

if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "submit.zip"
    w = sys.argv[2] if len(sys.argv) > 2 else "."
    try:
        check(d, w)
        print("PASS")
    except AssertionError as e:
        print("FAIL", e)
        sys.exit(1)
'''

# ===================== reference report =====================
REF_REPORT = {
    "report_overview": {
        "task": "Trace where the temperature parameter ptemp is used as a decision criterion in the SPICE simulation setup",
        "project_name": A_EXP["project_name"],
        "sim_file": "sim_p1_pl3.sp",
        "analysis_type": "parameter-usage-tracing / analysis-Q&A",
    },
    "ptemp_definition": {
        "file": "sim_p1_pl3.sp",
        "line": "15",
        "param_name": "ptemp",
        "value": "-40",
        "statement": ".param ptemp =-40",
        "directive_file": "sim_p1_pl3.sp",
        "directive_line": "41",
        "directive_value": "-40c",
    },
    "include_chain": {
        "sim_file": "sim_p1_pl3.sp",
        "include_line": "10",
        "included_file": "Pattern_Power_CRG.sp",
        "included_file_role": "power/voltage parameter table with temperature-conditional bias settings",
        "statement": '.inc "/proj/ddgoa/V0/workdir/ytzhu/simulation/setup/Pattern_Power_CRG.sp"',
    },
    "conditional_structure": {
        "outer_variable": "pvcc",
        "inner_variable": "ptemp",
        "nesting_description": "Two-level nested .if/.elseif/.else: outer bands on pvcc (supply voltage ranges), inner branches on ptemp (temperature) within each pvcc band",
        "outer_bands_count": 7,
        "bands": [
            {"pvcc_range": "0.9v-0.92v", "has_ptemp_branches": True},
            {"pvcc_range": "0.92v-0.97v", "has_ptemp_branches": True},
            {"pvcc_range": "0.97v-1.0v", "has_ptemp_branches": True},
            {"pvcc_range": "1.0v-1.1v", "has_ptemp_branches": True},
            {"pvcc_range": "1.1v-1.2v", "has_ptemp_branches": True},
            {"pvcc_range": "1.2v-1.4v", "has_ptemp_branches": True},
            {"pvcc_range": "1.4v-1.5v", "has_ptemp_branches": True},
        ],
    },
    "temperature_values": {
        "branch_values": ["-40", "98"],
        "default_branch": "else",
        "description": "ptemp==-40 (cold), ptemp==98 (hot), else (default/other temperatures)",
    },
    "controlled_parameters": {
        "params": ["pvwlp", "pvblh", "pvblhbk", "pvmwln", "pviso"],
        "values_per_branch": {
            "ptemp==-40": {"pvwlp": "2.8v", "pvblh": "0.9v", "pvblhbk": "0.9v", "pvmwln": "2.4v", "pviso": "1.44v"},
            "ptemp==98": {"pvwlp": "2.6v", "pvblh": "pvcc-0.05", "pvblhbk": "pvcc-0.05", "pvmwln": "2.2v", "pviso": "1.36v"},
            "else": {"pvwlp": "2.6v", "pvblh": "pvcc-0.05", "pvblhbk": "pvcc-0.05", "pvmwln": "2.2v", "pviso": "1.36v"},
        },
        "cold_vs_hot_difference": "Cold (ptemp==-40) uses higher pvwlp=2.8v and pviso=1.44v; hot (ptemp==98) uses lower pvwlp=2.6v and pviso=1.36v",
    },
    "mechanism": {
        "description": "ptemp is used as a decision criterion: within each pvcc voltage band, Pattern_Power_CRG.sp evaluates .if (ptemp==-40) / .elseif (ptemp==98) / .else and selects temperature-dependent bias voltages (pvwlp, pvblh, pvblhbk, pvmwln, pviso) accordingly.",
        "decision_role": "temperature-based selection of bias/supply voltage parameters for the CRG power table",
    },
    "ptemp_facts": dict(A_EXP),
    "evidence": [
        {"claim": "ptemp defined in sim_p1_pl3.sp", "source_file": "sim_p1_pl3.sp", "token": ".param ptemp =-40"},
        {"claim": "Pattern_Power_CRG.sp included from sim_p1_pl3.sp", "source_file": "sim_p1_pl3.sp", "token": '.inc "/proj/ddgoa/V0/workdir/ytzhu/simulation/setup/Pattern_Power_CRG.sp"'},
        {"claim": "first pvcc band opens with .if on pvcc", "source_file": "Pattern_Power_CRG.sp", "token": ".if ((pvcc  >=0.9v ) && (pvcc <= 0.92v ))"},
        {"claim": "ptemp==-40 cold branch", "source_file": "Pattern_Power_CRG.sp", "token": ".if (ptemp==-40)"},
        {"claim": "ptemp==98 hot branch", "source_file": "Pattern_Power_CRG.sp", "token": ".elseif (ptemp==98)"},
        {"claim": "cold pvwlp value", "source_file": "Pattern_Power_CRG.sp", "token": ".param  pvwlp       =  2.8v"},
        {"claim": "hot pviso value", "source_file": "Pattern_Power_CRG.sp", "token": ".param  pviso       =  1.36v"},
        {"claim": "simulator temp directive", "source_file": "sim_p1_pl3.sp", "token": ".temp -40c"},
    ],
    "conclusion": {
        "verdict": "ptemp is used as a temperature decision criterion in Pattern_Power_CRG.sp (included from sim_p1_pl3.sp line 10), selecting bias voltages across 7 pvcc bands via .if(ptemp==-40)/.elseif(ptemp==98)/.else.",
        "summary": "The temperature parameter ptemp=-40 (defined at sim_p1_pl3.sp:15) flows through the .inc include of Pattern_Power_CRG.sp, where it gates temperature-dependent bias voltage selection in nested .if/.elseif/.else blocks within each pvcc supply band.",
    },
    "methodology": "Read sim_p1_pl3.sp to locate ptemp definition and .inc chain; followed the include to Pattern_Power_CRG.sp; parsed the two-level .if/.elseif/.else conditional structure (outer pvcc bands x inner ptemp branches); extracted the temperature-controlled bias parameters and their cold/hot values; verified each claim against the source files.",
    "confidence": "high",
}

def make_report_zip(report_dict):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("ptemp_usage_analysis_report.json", json.dumps(report_dict, ensure_ascii=False, indent=2))
    return buf.getvalue()

def neg_empty():
    return make_report_zip({})
def neg_wrong_value():
    r = json.loads(json.dumps(REF_REPORT))
    r["ptemp_definition"]["value"] = "25"
    return make_report_zip(r)
def neg_no_evidence():
    r = json.loads(json.dumps(REF_REPORT))
    r["evidence"] = []
    return make_report_zip(r)
def neg_b_overfit():
    r = json.loads(json.dumps(REF_REPORT))
    r["ptemp_facts"] = dict(B_EXP)
    return make_report_zip(r)
def neg_no_condstruct():
    r = json.loads(json.dumps(REF_REPORT))
    r["conditional_structure"] = {}
    return make_report_zip(r)
def fake_no_report():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("readme.txt", "nothing here")
    return buf.getvalue()
def fake_minimal():
    return make_report_zip({"conclusion": {"verdict": "x"}, "confidence": "high", "methodology": "m"})
def fake_no_facts():
    r = json.loads(json.dumps(REF_REPORT))
    del r["ptemp_facts"]
    return make_report_zip(r)

NEG_ZIPS = [
    ("neg1_b_empty.zip", neg_empty()),
    ("neg2_c_wrong_value.zip", neg_wrong_value()),
    ("neg3_l_no_evidence.zip", neg_no_evidence()),
    ("neg4_n_b_overfit.zip", neg_b_overfit()),
    ("neg5_f_no_condstruct.zip", neg_no_condstruct()),
    ("fake1_a_no_report.zip", fake_no_report()),
    ("fake2_b_minimal.zip", fake_minimal()),
    ("fake3_m_no_facts.zip", fake_no_facts()),
]

NEG_SELFTEST = '''import subprocess, sys, os, re
REF = "reference_submit.zip"
NEG_DIR = "negative"
CHECK = "check.py"
def run_check(zip_path):
    p = zip_path if zip_path == REF or zip_path.startswith(NEG_DIR) else os.path.join(NEG_DIR, zip_path)
    r = subprocess.run([sys.executable, CHECK, p, "."], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr
rc, out = run_check(REF)
assert rc == 0, "reference must PASS but got rc=%d out=%s" % (rc, out[:500])
m = re.search(r"ALL PASS \\((\\d+)/(\\d+)\\)", out)
ref_n = int(m.group(2)) if m else 0
print("reference: ALL PASS (%d/%d)" % (ref_n, ref_n))
fail_labels = set()
for fn in sorted(os.listdir(NEG_DIR)):
    if not fn.endswith(".zip"):
        continue
    rc, out = run_check(fn)
    if rc == 0:
        raise AssertionError("NEG %r unexpectedly PASSED" % fn)
    mm = re.search(r"FAIL (?:at condition|check failed at) ([a-z])", out)
    lbl = mm.group(1) if mm else "?"
    fail_labels.add(lbl)
    print("neg %-40s FAIL at [%s]" % (fn, lbl))
print("negatives+fakes: all FAIL; distinct failing-condition labels = %s" % sorted(fail_labels))
print("NEGATIVE SELFTEST OK")
'''

PROMPT = """项目背景：用户 ghyang 在 FineSim/SPICE 仿真工程里用一个 .sp 仿真主文件跑 DDR5/CRG 仿真，文件路径：

/proj/ddgoa/V0/workdir/ghyang/DDGOA/Yiotwist_case4/sim_p1_pl3.sp

用户原话（逐字保留）：
> /proj/ddgoa/V0/workdir/ghyang/DDGOA/Yiotwist_case4/sim_p1_pl3.sp这个文件中定义了温度，我想知道这个温度在哪里被作为判断依据起了作用

任务：阅读附件中的 sim_p1_pl3.sp 与它通过 .inc 包含进来的 Pattern_Power_CRG.sp，追踪「温度参数 ptemp」在哪里被作为判断依据（decision criterion）起作用——即 ptemp 在哪个文件、哪一行定义，通过什么路径被引用，在什么样的条件结构里被用来选择什么。讲清楚完整的引用链与条件判断逻辑。

交付要求：
- 把分析结果写成一个结构化 JSON 报告，文件名 `ptemp_usage_analysis_report.json`，打包进 `outputs/submit.zip`。
- 报告必须能独立支撑以下判断：ptemp 的定义位置（文件/行/值）、它被引用的 include 链、它所参与的 .if/.elseif/.else 条件结构（外层变量、内层变量、band 数量）、被它控制的参数及其在不同温度分支下的取值、它作为判断依据的机制、以及能锚定到附件源文件的证据。
- 报告须含一个 `ptemp_facts` 结构化字段，记录从源文件解析出的关键事实（project_name / ptemp_value / temp_directive / power_table_file / pvcc_band_count / ptemp_branch_values / controlled_params / cold_pvwl_value / hot_pviso_value），用于校验。
- 仿真源文件已作为附件提供（assets/inputs/），按需查阅。

（这是用户 ghyang 的原始任务，逐字保留用户原话；用户最终要的是一份追踪 ptemp 用法的分析报告。）
"""

TASK_BRIEF = """# PtempCondUsageAnalyze-001 — SPICE ptemp 温度参数用法追踪（C-A analysis-Q&A）

## 用户原始任务（trace-faithful A 档，逐字）
> /proj/ddgoa/V0/workdir/ghyang/DDGOA/Yiotwist_case4/sim_p1_pl3.sp这个文件中定义了温度，我想知道这个温度在哪里被作为判断依据起了作用

## 项目
FineSim/SPICE 仿真工程，主仿真文件 sim_p1_pl3.sp（用户 ghyang，ddgoa DDR5/CRG 工程），通过 .inc 包含 Pattern_Power_CRG.sp（电源/偏置参数表）。

## 交付物
单文件 `ptemp_usage_analysis_report.json`（结构化 JSON），打包进 `outputs/submit.zip`。
报告应包含：report_overview、ptemp_definition（文件/行/值）、include_chain（.inc 引用链）、conditional_structure（外层 pvcc bands × 内层 ptemp 分支的 .if/.elseif/.else 结构）、temperature_values（分支值）、controlled_parameters（被 ptemp 控制的偏置参数及各分支取值）、mechanism（ptemp 作为判断依据的机制）、ptemp_facts（9 个 anti-hardcode 维度）、evidence（锚定附件文件名:token）、conclusion、methodology、confidence。
"""

HIDDEN_MANIFEST = {
    "case_id": CASE_ID,
    "hidden_input": "B_SPEC (base64-inlined in check.py)",
    "b_spec_summary": "Synthetic SPICE variant: drgsa_b project, ptemp=125, Pattern_Power_DDR.sp, 5 pvcc bands, branches ptemp==125/-25, params pvwl/pvbl/pvblbk/pvmwl/pvso",
    "anti_hardcode_dims": ANTI_DIMS,
    "a_b_diffs": diffs,
}

ATTACHMENTS = ["prompt.txt", "task_brief.md", "inputs/sim_p1_pl3.sp", "inputs/Pattern_Power_CRG.sp"]
TEST_RATIONALE = (
    "16 条断言：①(a) submit.zip 存在、合法 zip、含 ptemp_usage_analysis_report.json 且为合法 JSON 对象 "
    "②(b) report 含 >=8 个必需顶层段 (report_overview/ptemp_definition/include_chain/conditional_structure/temperature_values/controlled_parameters/mechanism/ptemp_facts/evidence/conclusion) "
    "③(c) ptemp_definition.file=sim_p1_pl3.sp 且 param_name=ptemp 且 value=-40 "
    "④(d) ptemp_definition.line=15 (定位 .param ptemp=-40) "
    "⑤(e) include_chain: Pattern_Power_CRG.sp 经 .inc 从 sim_p1_pl3.sp 引入 "
    "⑥(f) conditional_structure 描述外层 pvcc × 内层 ptemp 的 .if/.elseif/.else 两层嵌套 "
    "⑦(g) conditional_structure.outer_bands_count>=6 (实际 7 个含 ptemp 分支的 pvcc band) "
    "⑧(h) temperature_values 含 -40 与 98 两个分支值 (+else) "
    "⑨(i) controlled_parameters 含 >=4 个 {pvwlp,pvblh,pvblhbk,pvmwln,pviso} "
    "⑩(j) controlled_parameters 体现 cold(2.8/1.44) vs hot(2.6/1.36) 取值差异 "
    "⑪(k) mechanism 说明 ptemp 作为判断依据选择温度相关偏置电压 "
    "⑫(l) evidence >=4 条且每条 source_file 属 A 文件、token 为该 A 文件真实子串 "
    "⑬(m) ptemp_facts 全部 9 个 anti-hardcode 维度已填充 "
    "⑭(n) B judge-self-check: ptemp_facts 匹配 A-truth >=6/8 维 且 不同于隐藏 B-truth >=6/9 维 "
    "⑮(o) 3-seed 确定性: 打乱 B_SPEC manual_text 3 次, _parse_b 顺序无关, B truth sha256 稳定 "
    "⑯(p) conclusion.verdict 非空 + confidence in {high,medium,low} + methodology 非空"
)

JSONL_ENTRY = {
    "id": CASE_ID,
    "task_id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "task_brief": TASK_BRIEF,
    "test": CHECK_PY,
    "attachments": ATTACHMENTS,
    "metadata": {
        "domain": DOMAIN,
        "trace_source": TRACE,
        "test_rationale": TEST_RATIONALE,
    },
}

OUT = WORK + "/out/case"
ASSETS = OUT + "/assets/" + CASE_ID
REFD = OUT + "/reference/" + CASE_ID
os.makedirs(ASSETS + "/inputs", exist_ok=True)
os.makedirs(ASSETS + "/hidden", exist_ok=True)
os.makedirs(REFD + "/negative", exist_ok=True)

open(ASSETS + "/prompt.txt", "w").write(PROMPT)
open(ASSETS + "/task_brief.md", "w").write(TASK_BRIEF)
open(ASSETS + "/inputs/sim_p1_pl3.sp", "w").write(sim_a)
open(ASSETS + "/inputs/Pattern_Power_CRG.sp", "w").write(pow_a)
open(ASSETS + "/hidden/b_spec.json", "w").write(json.dumps(B_SPEC, ensure_ascii=False, indent=2))
open(ASSETS + "/hidden/hidden_manifest.json", "w").write(json.dumps(HIDDEN_MANIFEST, ensure_ascii=False, indent=2))

open(REFD + "/check.py", "w").write(CHECK_PY)
open(REFD + "/a_files.json", "w").write(json.dumps(A_FILES, ensure_ascii=False, indent=2))
open(REFD + "/b_spec.json", "w").write(json.dumps(B_SPEC, ensure_ascii=False, indent=2))
open(REFD + "/reference_submit.zip", "wb").write(make_report_zip(REF_REPORT))
open(REFD + "/ptemp_usage_analysis_report.json", "w").write(json.dumps(REF_REPORT, ensure_ascii=False, indent=2))
for name, data in NEG_ZIPS:
    open(REFD + "/negative/" + name, "wb").write(data)
open(REFD + "/negative/negative_selftest.py", "w").write(NEG_SELFTEST)

open(WORK + "/out/jsonl_entry.json", "w").write(json.dumps(JSONL_ENTRY, ensure_ascii=False))

# ===================== self-verify on .75 =====================
print("\n=== SELF-VERIFY ===")
os.chdir(REFD)
rc = subprocess.run([sys.executable, "check.py", "reference_submit.zip", "."], capture_output=True, text=True)
print("REF check rc=%d" % rc.returncode)
print(rc.stdout[-1800:])
if rc.returncode != 0:
    print("STDERR:", rc.stderr[-800:])
    raise SystemExit("REFERENCE FAILED")
rc2 = subprocess.run([sys.executable, "negative/negative_selftest.py"], capture_output=True, text=True)
print("NEG selftest rc=%d" % rc2.returncode)
print(rc2.stdout[-1500:])
if rc2.returncode != 0:
    print("STDERR:", rc2.stderr[-800:])
    raise SystemExit("NEGATIVE SELFTEST FAILED")

# §4.9 three fakes already in negatives; verify they FAIL (covered by selftest)
# pack tarball
os.chdir(WORK + "/out")
with tarfile.open("case.tar.gz", "w:gz") as tf:
    tf.add("case")
print("\n=== DONE: case.tar.gz written ===")
print("check.py size:", len(CHECK_PY))
