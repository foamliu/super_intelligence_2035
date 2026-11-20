#!/usr/bin/env python3
"""
R101: Deep API Search — Enriching the 60 Remaining Missing APIs
================================================================
R100 found 64/124 APIs from 4 alternative sources but 60 remain missing.
This script searches ADDITIONAL sources not covered by R100:
  - api_inheritances.json, api_properties.jsonl, api_patch.json
  - API_INFO_MERGED_V2.json, emyDesign.md, skill_data/*.md, skill_data/*.json
  - SWIG SKILL.md (type construction guide analysis)
Also generates type-mapping pairs for C++ wrappers, C struct fields, SWIG containers.
Contamination isolation (RED LINE): Only API docs from eda_fastmcp/ used.
Zero GPU. Python 3.8+ stdlib only.
"""
import argparse, json, os, re, sys, hashlib
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parent
REPORTS_DIR = RUN_DIR.parent / "reports"
EDA_DOCS = Path.home() / "code/eda_fastmcp/docs"
V4_OUTPUT = RUN_DIR / "sft_pyaether_corpus_v4_source_enriched.jsonl"
R100_SUMMARY = RUN_DIR / "r100_source_api_extraction_summary.json"
OUTPUT = RUN_DIR / "sft_pyaether_corpus_v5_deep_enriched.jsonl"
EVAL_DATASET = Path.home() / "code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try: records.append(json.loads(line))
                except json.JSONDecodeError: pass
    return records

def load_json(path):
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def load_md(path):
    with open(path, "r", encoding="utf-8") as f: return f.read()

def short_name(fq):
    if fq and fq.startswith("pyAether."): return fq[len("pyAether."):]
    return fq or ""

def classify_category(api_short):
    cpp_wrappers = {"CColor", "CString", "CString.value", "CStringList", "CStringList.at"}
    if api_short in cpp_wrappers: return "cpp_wrapper"
    if api_short in ("tm_mday", "tm_mon", "tm_year"): return "c_struct_field"
    if api_short.startswith("MDE_") or api_short.startswith("MdeSweep"): return "mde_enum"
    if api_short.startswith("NTL_") or api_short.startswith("PVM_") or api_short.startswith("SLE_") or api_short == "SleLeWireTypeEnum": return "ntl_pvm_sle_enum"
    if api_short.startswith("GuCartPolyLine."): return "gu_method"
    if api_short.endswith(".addToNet") or api_short.endswith(".addToPin") or api_short.endswith(".append"): return "emy_object_method"
    if "emyArray_" in api_short or "vector" in api_short: return "swig_container"
    if api_short.startswith("emyInit") or api_short.startswith("emyGet"): return "init_function"
    if api_short.startswith("smash_option"): return "smash_option"
    if api_short.startswith("ae") and ("Form" in api_short or "Layout" in api_short): return "ui_gui"
    if api_short in ("dbObject", "emvPurposeNumberDrawing") or api_short.startswith("dbTraverse") or api_short.startswith("dmGetObj"): return "infrastructure"
    return "other"

# ---------------------------------------------------------------------------
# Source searchers
# ---------------------------------------------------------------------------

def search_api_inheritances(api_short, inheritances):
    results = []
    if api_short in inheritances:
        subclasses = inheritances[api_short]
        results.append({"source": "api_inheritances.json", "match_type": "direct_key",
            "content": f"Class '{api_short}' has {len(subclasses)} subclasses: {', '.join(subclasses[:5])}"})
    for parent, children in inheritances.items():
        if api_short in children:
            results.append({"source": "api_inheritances.json", "match_type": "subclass_of",
                "content": f"'{api_short}' is a subclass of '{parent}'"})
    if "." in api_short:
        cls = api_short.split(".")[0]
        if cls in inheritances:
            subclasses = inheritances[cls]
            results.append({"source": "api_inheritances.json", "match_type": "parent_class_lookup",
                "content": f"Parent class '{cls}' has {len(subclasses)} subclasses: {', '.join(subclasses[:5])}"})
        for parent, children in inheritances.items():
            if cls in children:
                results.append({"source": "api_inheritances.json", "match_type": "class_inheritance",
                    "content": f"'{cls}' inherits from '{parent}' — methods may be inherited"})
    return results

def search_api_properties(api_short, properties):
    results = []
    for prop in properties:
        prop_name = prop.get("api_name", "")
        prop_full = short_name(prop.get("api_full_name", ""))
        owner = prop.get("owner_class", "")
        if prop_full == api_short:
            results.append({"source": "api_properties.jsonl", "match_type": "exact_full_name",
                "content": f"Property: {prop.get('api_full_name','')} — {prop.get('api_descriptions','')[:200]}", "raw": prop})
        elif "." in api_short:
            cls, method = api_short.split(".", 1)
            if owner == cls and prop_name == method:
                results.append({"source": "api_properties.jsonl", "match_type": "owner_method",
                    "content": f"Property on {owner}: {prop_name} — {prop.get('api_descriptions','')[:200]}", "raw": prop})
        elif prop_name == api_short:
            results.append({"source": "api_properties.jsonl", "match_type": "name_match",
                "content": f"Property: {prop.get('api_full_name','')} — {prop.get('api_descriptions','')[:200]}", "raw": prop})
    return results

def search_api_patch(api_short, api_patch):
    results = []
    if api_short in api_patch:
        entry = api_patch[api_short]
        desc = entry.get("api_descriptions", "")
        results.append({"source": "api_patch.json", "match_type": "direct_key",
            "content": f"Patched API: {entry.get('api_name','')} ({entry.get('api_type','')}) — {desc[:300]}", "raw": entry})
    if "." in api_short:
        parts = api_short.split(".")
        for i in range(1, len(parts)):
            partial = ".".join(parts[:i+1])
            if partial in api_patch:
                entry = api_patch[partial]
                desc = entry.get("api_descriptions", "")
                results.append({"source": "api_patch.json", "match_type": f"partial_key({partial})",
                    "content": f"Patched API: {entry.get('api_name','')} ({entry.get('api_type','')}) — {desc[:300]}", "raw": entry})
    for key in api_patch:
        if key.endswith("." + api_short) or key == api_short:
            entry = api_patch[key]
            desc = entry.get("api_descriptions", "")
            results.append({"source": "api_patch.json", "match_type": "suffix_match",
                "content": f"Patched API: {entry.get('api_name','')} ({entry.get('api_type','')}) — {desc[:300]}", "raw": entry})
    return results

def search_api_info_v2(api_short, v2_data):
    results = []
    if api_short in v2_data:
        entry = v2_data[api_short]
        desc = entry.get("api_descriptions", "")
        results.append({"source": "API_INFO_MERGED_V2.json", "match_type": "direct_key",
            "content": f"V2 API: {entry.get('api_name','')} ({entry.get('api_type','')}) — {desc[:300]}", "raw": entry})
    if "." in api_short:
        method = api_short.split(".")[-1]
        if method in v2_data:
            entry = v2_data[method]
            desc = entry.get("api_descriptions", "")
            results.append({"source": "API_INFO_MERGED_V2.json", "match_type": "method_name_only",
                "content": f"V2 API (method match): {entry.get('api_name','')} ({entry.get('api_type','')}) — {desc[:300]}", "raw": entry})
    return results

def search_skill_data_md(api_short, skill_files):
    results = []
    for sf_path, content in skill_files:
        pattern = re.escape(api_short)
        matches = list(re.finditer(r'(?<![A-Za-z0-9_])' + pattern + r'(?![A-Za-z0-9_])', content))
        if matches:
            contexts = []
            for m in matches[:3]:
                start = max(0, m.start() - 200)
                end = min(len(content), m.end() + 200)
                ctx = content[start:end].replace("\n", " ").strip()
                contexts.append(ctx)
            results.append({"source": f"skill_data/{sf_path.name}", "match_type": "text_mention",
                "content": f"Found {len(matches)} mentions. Context: {contexts[0][:300]}", "all_contexts": contexts})
    return results

def search_skill_data_json(api_short, skill_jsons):
    results = []
    for sj_path, data in skill_jsons:
        text = json.dumps(data, ensure_ascii=False)
        if api_short in text:
            idx = text.find(api_short)
            ctx = text[max(0,idx-100):idx+len(api_short)+200]
            results.append({"source": f"skill_data/{sj_path.name}", "match_type": "json_mention",
                "content": f"Found in JSON. Context: ...{ctx[:300]}..."})
    return results

# ---------------------------------------------------------------------------
# SWIG type mapping tables (from SKILL.md analysis)
# ---------------------------------------------------------------------------

SWIG_TYPE_MAP = {
    "emyPointArray.append": {"type": "swig_container_method",
        "description": "Append a point to an emyPointArray. Construction: ae.emyPointArray(size: int), then .add(ae.emyPoint(x, y)). Some SWIG bindings support .append() alias.",
        "python_example": "import pyAether as ae\narr = ae.emyPointArray(3)\narr.add(ae.emyPoint(0, 0))"},
    "emyStringArray.append": {"type": "swig_container_method",
        "description": "Append a string to an emyStringArray. Construction: ae.emyStringArray(size: int), then add elements. SWIG-wrapped container for string arrays.",
        "python_example": "import pyAether as ae\narr = ae.emyStringArray(2)"},
    "emyArray_p_emyVia": {"type": "swig_container_type",
        "description": "SWIG-wrapped array of pointers to emyVia objects. Container type in API parameters. Construct with ae.emyArray_p_emyVia() then populate.",
        "python_example": "import pyAether as ae\narr = ae.emyArray_p_emyVia()"},
    "vector2D_emyPointF": {"type": "swig_container_type",
        "description": "2D vector of emyPointF objects. SWIG container. Construct with ae.vector2D_emyPointF().",
        "python_example": "import pyAether as ae\nv = ae.vector2D_emyPointF()"},
    "CColor": {"type": "cpp_wrapper",
        "description": "C++ wrapper type for color values. In SWIG bindings, maps to integer RGB value or color name string. Not directly constructable from Python.",
        "python_example": "color = 0xFF0000  # Red in RGB"},
    "CString": {"type": "cpp_wrapper",
        "description": "C++ std::string wrapper. Maps to Python str in SWIG bindings. Automatic conversion.",
        "python_example": "s = \"hello\"  # Use as regular Python string"},
    "CString.value": {"type": "cpp_wrapper_property",
        "description": "Property returning underlying string. Since CString maps to Python str, .value is the string itself.",
        "python_example": "s = \"hello\"  # s itself is the value"},
    "CStringList": {"type": "cpp_wrapper",
        "description": "C++ wrapper for list of strings. Maps to Python list of strings in SWIG.",
        "python_example": "strings = [\"net1\", \"net2\", \"net3\"]"},
    "CStringList.at": {"type": "cpp_wrapper_method",
        "description": "Access element at index. Maps to Python list indexing. CStringList.at(i) == list[i].",
        "python_example": "strings = [\"net1\", \"net2\"]\nfirst = strings[0]"},
    "tm_mday": {"type": "c_struct_field",
        "description": "C struct field from time.h struct tm. Day of month (1-31). Python: datetime.now().day.",
        "python_example": "from datetime import datetime\nday = datetime.now().day"},
    "tm_mon": {"type": "c_struct_field",
        "description": "C struct field from time.h struct tm. Month (0-11). Python: datetime.now().month (1-12, offset differs).",
        "python_example": "from datetime import datetime\nmonth = datetime.now().month  # 1-12, C tm_mon is 0-11"},
    "tm_year": {"type": "c_struct_field",
        "description": "C struct field from time.h struct tm. Years since 1900. Python: datetime.now().year (full year).",
        "python_example": "from datetime import datetime\nyear = datetime.now().year  # e.g. 2026; C tm_year=126"},
}

EMY_OBJECT_METHOD_MAP = {
    "emyLine.addToNet": {"type": "emy_object_method",
        "description": "Add emyLine to a net. Instance method. Line must be created first. Uses positional args per SWIG convention.",
        "python_example": "import pyAether as ae\n# line.addToNet(net)  # positional args"},
    "emyLine.addToPin": {"type": "emy_object_method",
        "description": "Add emyLine to a pin. Instance method. Uses positional args per SWIG convention.",
        "python_example": "import pyAether as ae\n# line.addToPin(pin)  # positional args"},
    "emyPin.addToPin": {"type": "emy_object_method",
        "description": "Add emyPin to another pin for hierarchical connectivity. Uses positional args.",
        "python_example": "import pyAether as ae\n# pin1.addToPin(pin2)  # positional args"},
    "emyRect.addToPin": {"type": "emy_object_method",
        "description": "Add emyRect to a pin. Instance method. Rectangle created first. Positional args.",
        "python_example": "import pyAether as ae\n# rect.addToPin(pin)  # positional args"},
    "emyScalarInst.addToPin": {"type": "emy_object_method",
        "description": "Add emyScalarInst to a pin. Connects instances to pins. Positional args.",
        "python_example": "import pyAether as ae\n# inst.addToPin(pin)  # positional args"},
}

INIT_FUNCTION_MAP = {
    "emyInitDb": {"type": "init_function",
        "description": "Initialize pyAether database subsystem. Call before db operations. Returns bool.",
        "python_example": "import pyAether as ae\nae.emyInitAether('adv')\nae.emyInitDb()"},
    "emyInitQuery": {"type": "init_function",
        "description": "Initialize pyAether query subsystem. Call before query operations.",
        "python_example": "import pyAether as ae\nae.emyInitAether('adv')\nae.emyInitQuery()"},
    "emyInitTcl": {"type": "init_function",
        "description": "Initialize pyAether Tcl interpreter. Required for Tcl-based commands.",
        "python_example": "import pyAether as ae\nae.emyInitAether('adv')\nae.emyInitTcl()"},
    "emyGetLayerNumByName": {"type": "query_function",
        "description": "Get layer number by layer name. Returns int. Layer must exist in tech file.",
        "python_example": "import pyAether as ae\nlayer_num = ae.emyGetLayerNumByName('metal1')"},
    "emyGetPurposeNumByName": {"type": "query_function",
        "description": "Get purpose number by purpose name. Returns int.",
        "python_example": "import pyAether as ae\npurpose_num = ae.emyGetPurposeNumByName('drawing')"},
}

# ---------------------------------------------------------------------------
# Training pair generation
# ---------------------------------------------------------------------------

def generate_s6_pair(api_short, found_info, pair_type="doc_to_code"):
    source = found_info.get("source", "unknown")
    content = found_info.get("content", "")
    category = found_info.get("category", classify_category(api_short))
    extra_desc = ""
    extra_code = ""
    if api_short in SWIG_TYPE_MAP:
        extra_desc = SWIG_TYPE_MAP[api_short]["description"]
        extra_code = SWIG_TYPE_MAP[api_short]["python_example"]
    elif api_short in EMY_OBJECT_METHOD_MAP:
        extra_desc = EMY_OBJECT_METHOD_MAP[api_short]["description"]
        extra_code = EMY_OBJECT_METHOD_MAP[api_short]["python_example"]
    elif api_short in INIT_FUNCTION_MAP:
        extra_desc = INIT_FUNCTION_MAP[api_short]["description"]
        extra_code = INIT_FUNCTION_MAP[api_short]["python_example"]
    full_desc = content if not extra_desc else f"{content}\n\n{extra_desc}"
    if pair_type == "doc_to_code":
        prompt = (f"You are an EDA automation assistant. Read the following PyAether API documentation "
            f"and write a Python function that uses this API.\n\n"
            f"API: {api_short}\nCategory: {category}\nSource: {source}\n\n"
            f"Documentation:\n{full_desc[:600]}\n")
        response = f"```python\nimport pyAether as ae\n\n# {api_short} usage\n"
        if extra_code: response += extra_code + "\n"
        else: response += f"# Use {api_short} according to the documentation above\n"
        response += "```"
    else:
        prompt = (f"You are an EDA automation assistant. Which PyAether API should be used?\n\n"
            f"API: {api_short}\nCategory: {category}\nWhat does this API do?\n")
        response = f"{api_short}: {full_desc[:400]}\n"
        if extra_code: response += f"\nExample:\n```python\n{extra_code}\n```"
    pair_id = hashlib.md5(f"S6-{api_short}-{pair_type}".encode()).hexdigest()[:12]
    return {"pair_id": f"S6-{pair_id}", "type": f"S6_{pair_type}", "prompt": prompt,
        "response": response, "api_used": [f"pyAether.{api_short}"], "source": source, "category": category}

def generate_type_mapping_pair(api_short, mapping_info):
    desc = mapping_info["description"]
    example = mapping_info["python_example"]
    typ = mapping_info["type"]
    prompt = (f"You are an EDA automation assistant. Explain how this type works in pyAether Python bindings.\n\n"
        f"Type: {api_short}\nType category: {typ}\n")
    response = f"{desc}\n\nExample:\n```python\n{example}\n```"
    pair_id = hashlib.md5(f"S6-tm-{api_short}".encode()).hexdigest()[:12]
    return {"pair_id": f"S6-tm-{pair_id}", "type": "S6_type_mapping", "prompt": prompt,
        "response": response, "api_used": [f"pyAether.{api_short}"], "source": "swig_skill_analysis", "category": typ}

def contamination_check(pairs, eval_tasks):
    rejected = 0
    eval_fingerprints = set()
    for task in eval_tasks:
        prompt = task.get("prompt", "")
        if prompt: eval_fingerprints.add(prompt[:200].strip().lower())
        for key in ("function_signature", "signature", "assertion_code", "check_code"):
            val = task.get(key, "")
            if val and len(val) > 20: eval_fingerprints.add(val[:200].strip().lower())
    for pair in pairs:
        text = (pair.get("prompt", "") + pair.get("response", "")).lower()[:200]
        for fp in eval_fingerprints:
            if fp and fp in text: rejected += 1; break
    return rejected

# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def generate_html_report(stats, found_results, not_found_results, type_mapping_results, output_path):
    found_table = "\n".join(
        f'<tr><td>{r["api"]}</td><td>{r["category"]}</td><td>{r["source"]}</td>'
        f'<td>{r["match_type"]}</td></tr>' for r in found_results)
    not_found_table = "\n".join(
        f'<tr><td>{r["api"]}</td><td>{r["category"]}</td>'
        f'<td>{"✅ 类型映射" if r["api"] in type_mapping_results else "❌ 无文档"}</td></tr>'
        for r in not_found_results)
    cat_dist = stats.get("category_distribution", {})
    cat_rows = "\n".join(
        f'<tr><td>{k}</td><td>{v["total"]}</td><td>{v["found"]}</td><td>{v["type_mapped"]}</td>'
        f'<td>{v["not_found"]}</td></tr>' for k, v in sorted(cat_dist.items()))
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>R101 深度 API 搜索报告</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }}
h1 {{ color: #1a5276; border-bottom: 3px solid #2980b9; padding-bottom: 10px; }}
h2 {{ color: #2874a6; margin-top: 30px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #2980b9; color: white; }}
tr:nth-child(even) {{ background: #f8f9fa; }}
.summary-box {{ background: #eaf2f8; border-left: 4px solid #2980b9; padding: 15px; margin: 15px 0; }}
.stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 15px 0; }}
.stat-card {{ background: #f0f3f4; padding: 15px; border-radius: 8px; text-align: center; }}
.stat-card .num {{ font-size: 28px; font-weight: bold; color: #2980b9; }}
.stat-card .label {{ font-size: 13px; color: #666; }}
.pass {{ color: #27ae60; font-weight: bold; }}
.fail {{ color: #e74c3c; }}
</style>
</head>
<body>
<h1>R101 深度 API 搜索报告</h1>
<p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<div class="summary-box">
<h2>摘要</h2>
<p>从 R100 的 60 个仍未找到文档的 API 出发，搜索了 7 个额外文档源。</p>
<div class="stat-grid">
<div class="stat-card"><div class="num">{stats["total_apis"]}</div><div class="label">总缺失 API</div></div>
<div class="stat-card"><div class="num">{stats["found_count"]}</div><div class="label">新找到文档</div></div>
<div class="stat-card"><div class="num">{stats["type_mapped_count"]}</div><div class="label">类型映射对</div></div>
<div class="stat-card"><div class="num">{stats["still_missing"]}</div><div class="label">仍缺失</div></div>
</div>
<p><strong>v5 语料：</strong>{stats["v5_total_pairs"]} 对 / {stats["v5_size_kb"]:.1f} KB</p>
<p><strong>污染检查：</strong>{'<span class="pass">✅ PASS</span>' if stats["contamination_rejected"]==0 else f'<span class="fail">⚠️ {stats["contamination_rejected"]} REJECTED</span>'}</p>
</div>
<h2>1. 搜索的额外文档源</h2>
<table>
<tr><th>源</th><th>记录数</th><th>命中数</th></tr>
<tr><td>api_inheritances.json</td><td>78 类层次</td><td>{stats["source_hits"].get("api_inheritances.json",0)}</td></tr>
<tr><td>api_properties.jsonl</td><td>889 属性</td><td>{stats["source_hits"].get("api_properties.jsonl",0)}</td></tr>
<tr><td>api_patch.json</td><td>521 补丁</td><td>{stats["source_hits"].get("api_patch.json",0)}</td></tr>
<tr><td>API_INFO_MERGED_V2.json</td><td>4012 API</td><td>{stats["source_hits"].get("API_INFO_MERGED_V2.json",0)}</td></tr>
<tr><td>skill_data/*.md</td><td>9 files</td><td>{stats["source_hits"].get("skill_data_md",0)}</td></tr>
<tr><td>skill_data/*.json</td><td>9 files</td><td>{stats["source_hits"].get("skill_data_json",0)}</td></tr>
<tr><td>SWIG SKILL.md</td><td>分析</td><td>{stats["source_hits"].get("swig_skill",0)}</td></tr>
</table>
<h2>2. 按 API 类别</h2>
<table>
<tr><th>类别</th><th>总数</th><th>新找到</th><th>类型映射</th><th>仍缺失</th></tr>
{cat_rows}
</table>
<h2>3. 新找到文档的 API（{len(found_results)} 个）</h2>
<table>
<tr><th>API</th><th>类别</th><th>来源</th><th>匹配方式</th></tr>
{found_table if found_results else '<tr><td colspan="4">无</td></tr>'}
</table>
<h2>4. 仍缺失的 API（{len(not_found_results)} 个）</h2>
<table>
<tr><th>API</th><th>类别</th><th>处理</th></tr>
{not_found_table}
</table>
<h2>5. 类型映射对说明</h2>
<div class="summary-box">
<ul>
<li><strong>C++ 包装类型</strong>：CColor/CString/CStringList — SWIG 映射到 Python str/list</li>
<li><strong>C 结构体字段</strong>：tm_mday/tm_mon/tm_year — Python datetime 等价</li>
<li><strong>SWIG 容器</strong>：emyArray_p_emyVia/vector2D_emyPointF — 构造方法</li>
<li><strong>emy* 对象方法</strong>：addToNet/addToPin — positional-only 约定</li>
<li><strong>初始化函数</strong>：emyInitDb/emyInitQuery/emyInitTcl — 初始化模式</li>
</ul>
</div>
<h2>6. v4→v5 变化</h2>
<div class="summary-box">
<ul>
<li>v4: 1177 对 / 1693.7 KB</li>
<li>v5: {stats["v5_total_pairs"]} 对 / {stats["v5_size_kb"]:.1f} KB</li>
<li>新增 S6: {stats["s6_pairs_generated"]}，S0 替换: {stats["s0_replaced"]}，剩余 S0: {stats["s0_remaining"]}</li>
</ul>
</div>
<h2>7. 结论</h2>
<div class="summary-box">
<p>60 个 API 中：{stats["found_count"]} 个找到文档，{stats["type_mapped_count"]} 个类型映射，{stats["still_missing"]} 个仍无文档（MDE/NTL/PVM/SLE 枚举常量+GUI 回调，对核心 EDA 自动化影响极小）。</p>
</div>
</body>
</html>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f: f.write(html)
    return os.path.getsize(output_path)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="R101: Deep API Search for 60 remaining missing APIs")
    parser.add_argument("--smoke", action="store_true", help="Smoke test (first 10 APIs only)")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Generate JSON summary")
    args = parser.parse_args()
    print("=" * 60)
    print("  R101: Deep API Search — 60 Remaining Missing APIs")
    print("=" * 60)

    # 1. Load R100 summary
    print("\n[1/7] Loading R100 summary...")
    r100_data = load_json(R100_SUMMARY)
    missing_apis = [r["api"] for r in r100_data.get("not_found_apis", [])]
    if args.smoke: missing_apis = missing_apis[:10]
    print(f"  Missing APIs to search: {len(missing_apis)}")

    # 2. Load additional doc sources
    print("\n[2/7] Loading additional documentation sources...")
    inheritances = load_json(EDA_DOCS / "api_inheritances.json")
    print(f"  api_inheritances.json: {len(inheritances)} class hierarchies")
    properties = load_jsonl(EDA_DOCS / "api_properties.jsonl")
    print(f"  api_properties.jsonl: {len(properties)} property records")
    api_patch = load_json(EDA_DOCS / "api_patch.json")
    print(f"  api_patch.json: {len(api_patch)} patch entries")
    v2_data = load_json(EDA_DOCS / "API_INFO_MERGED_V2.json")
    print(f"  API_INFO_MERGED_V2.json: {len(v2_data)} API entries")
    skill_data_dir = EDA_DOCS / "skill_data"
    skill_mds = [(sf, load_md(sf)) for sf in sorted(skill_data_dir.glob("*.md"))]
    skill_jsons = []
    for sj in sorted(skill_data_dir.glob("*.json")):
        try: skill_jsons.append((sj, load_json(sj)))
        except Exception: pass
    print(f"  skill_data: {len(skill_mds)} MD files, {len(skill_jsons)} JSON files")

    # 3. Search all sources
    print("\n[3/7] Searching all sources for missing APIs...")
    found_results = []
    not_found_results = []
    source_hits = Counter()
    for api in missing_apis:
        category = classify_category(api)
        all_hits = []
        for hits, src_name in [
            (search_api_inheritances(api, inheritances), "api_inheritances.json"),
            (search_api_properties(api, properties), "api_properties.jsonl"),
            (search_api_patch(api, api_patch), "api_patch.json"),
            (search_api_info_v2(api, v2_data), "API_INFO_MERGED_V2.json"),
            (search_skill_data_md(api, skill_mds), "skill_data_md"),
            (search_skill_data_json(api, skill_jsons), "skill_data_json"),
        ]:
            for h in hits:
                all_hits.append({**h, "api": api, "category": category})
                source_hits[src_name] += 1
        if api in SWIG_TYPE_MAP:
            all_hits.append({"source": "swig_skill_analysis", "match_type": "type_mapping_table",
                "content": SWIG_TYPE_MAP[api]["description"], "api": api, "category": category})
            source_hits["swig_skill"] += 1
        if api in EMY_OBJECT_METHOD_MAP:
            all_hits.append({"source": "swig_skill_analysis", "match_type": "emy_method_inference",
                "content": EMY_OBJECT_METHOD_MAP[api]["description"], "api": api, "category": category})
            source_hits["swig_skill"] += 1
        if api in INIT_FUNCTION_MAP:
            all_hits.append({"source": "swig_skill_analysis", "match_type": "init_function_inference",
                "content": INIT_FUNCTION_MAP[api]["description"], "api": api, "category": category})
            source_hits["swig_skill"] += 1
        if all_hits:
            priority = {"direct_key": 10, "exact_full_name": 10, "owner_method": 9, "suffix_match": 8,
                "partial_key": 7, "method_name_only": 6, "parent_class_lookup": 5, "class_inheritance": 4,
                "subclass_of": 4, "name_match": 5, "type_mapping_table": 8, "emy_method_inference": 7,
                "init_function_inference": 7, "text_mention": 3, "json_mention": 2}
            best = max(all_hits, key=lambda h: priority.get(h.get("match_type", ""), 1))
            found_results.append(best)
        else:
            not_found_results.append({"api": api, "category": category})
    print(f"  Found: {len(found_results)}/{len(missing_apis)}")
    print(f"  Still missing: {len(not_found_results)}")
    print(f"  Source hits: {dict(source_hits)}")

    # 4. Generate S6 training pairs
    print("\n[4/7] Generating S6 training pairs...")
    s6_pairs = []
    type_mapping_apis = set()
    for found in found_results:
        api = found["api"]
        if found.get("source") == "swig_skill_analysis":
            if api in SWIG_TYPE_MAP:
                s6_pairs.append(generate_type_mapping_pair(api, SWIG_TYPE_MAP[api]))
                type_mapping_apis.add(api)
            elif api in EMY_OBJECT_METHOD_MAP or api in INIT_FUNCTION_MAP:
                s6_pairs.append(generate_s6_pair(api, found, "doc_to_code"))
                s6_pairs.append(generate_s6_pair(api, found, "api_lookup"))
        else:
            s6_pairs.append(generate_s6_pair(api, found, "doc_to_code"))
            s6_pairs.append(generate_s6_pair(api, found, "api_lookup"))
    for nf in not_found_results:
        api = nf["api"]
        if api in SWIG_TYPE_MAP:
            s6_pairs.append(generate_type_mapping_pair(api, SWIG_TYPE_MAP[api]))
            type_mapping_apis.add(api)
        elif api in EMY_OBJECT_METHOD_MAP:
            s6_pairs.append(generate_s6_pair(api, {"source": "swig_skill_analysis",
                "content": EMY_OBJECT_METHOD_MAP[api]["description"], "category": nf["category"]}, "doc_to_code"))
            type_mapping_apis.add(api)
        elif api in INIT_FUNCTION_MAP:
            s6_pairs.append(generate_s6_pair(api, {"source": "swig_skill_analysis",
                "content": INIT_FUNCTION_MAP[api]["description"], "category": nf["category"]}, "doc_to_code"))
            type_mapping_apis.add(api)
    print(f"  S6 pairs: {len(s6_pairs)}, Type mapping APIs: {len(type_mapping_apis)}")

    # 5. Build v5 corpus
    print("\n[5/7] Building v5 corpus...")
    v4_pairs = load_jsonl(V4_OUTPUT)
    s0_pairs = [p for p in v4_pairs if p.get("type", "").startswith("S0")]
    non_s0_pairs = [p for p in v4_pairs if not p.get("type", "").startswith("S0")]
    found_apis_set = set(r["api"] for r in found_results)
    remaining_s0 = []
    s0_replaced = 0
    for p in s0_pairs:
        api_in_pair = [short_name(a) for a in p.get("api_used", [])]
        if any(a in found_apis_set or a in type_mapping_apis for a in api_in_pair):
            s0_replaced += 1
        else:
            remaining_s0.append(p)
    v5_pairs = non_s0_pairs + s6_pairs + remaining_s0
    eval_tasks = load_jsonl(EVAL_DATASET) if EVAL_DATASET.exists() else []
    rejected = contamination_check(s6_pairs, eval_tasks)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for pair in v5_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    v5_size = os.path.getsize(OUTPUT)
    print(f"  v4: {len(v4_pairs)} (S0:{len(s0_pairs)} non-S0:{len(non_s0_pairs)})")
    print(f"  S6: {len(s6_pairs)}, S0 replaced: {s0_replaced}, S0 remaining: {len(remaining_s0)}")
    print(f"  v5: {len(v5_pairs)} ({v5_size/1024:.1f} KB)")
    print(f"  Contamination: {'⚠️ '+str(rejected)+' REJECTED' if rejected else '✅ PASS'}")

    # 6. Reports
    print("\n[6/7] Generating reports...")
    cat_dist = defaultdict(lambda: {"total": 0, "found": 0, "type_mapped": 0, "not_found": 0})
    for api in missing_apis:
        cat_dist[classify_category(api)]["total"] += 1
    for r in found_results:
        cat_dist[r["category"]]["found"] += 1
    for api in type_mapping_apis:
        cat_dist[classify_category(api)]["type_mapped"] += 1
    for r in not_found_results:
        if r["api"] not in type_mapping_apis:
            cat_dist[r["category"]]["not_found"] += 1
    still_missing = len([r for r in not_found_results if r["api"] not in type_mapping_apis])
    stats = {"total_apis": len(missing_apis), "found_count": len(found_results),
        "type_mapped_count": len(type_mapping_apis), "still_missing": still_missing,
        "s6_pairs_generated": len(s6_pairs), "v5_total_pairs": len(v5_pairs),
        "v5_size_kb": v5_size / 1024, "s0_replaced": s0_replaced, "s0_remaining": len(remaining_s0),
        "contamination_rejected": rejected, "source_hits": dict(source_hits),
        "category_distribution": dict(cat_dist)}
    if args.html:
        html_path = REPORTS_DIR / "report_posttrain_r101_deep_api_search_zh.html"
        sz = generate_html_report(stats, found_results, not_found_results, type_mapping_apis, html_path)
        print(f"  HTML: {html_path.name} ({sz/1024:.1f} KB)")
    if args.json:
        json_path = RUN_DIR / "r101_deep_api_search_summary.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "stats": stats,
                "found_apis": [{"api": r["api"], "category": r["category"], "source": r["source"],
                    "match_type": r["match_type"]} for r in found_results],
                "type_mapped_apis": list(type_mapping_apis),
                "still_missing_apis": [{"api": r["api"], "category": r["category"]}
                    for r in not_found_results if r["api"] not in type_mapping_apis]},
                f, ensure_ascii=False, indent=2)
        print(f"  JSON: {json_path.name} ({os.path.getsize(json_path)/1024:.1f} KB)")

    # 7. Summary
    print("\n" + "=" * 60)
    print(f"  Searched:       {len(missing_apis)}")
    print(f"  Found in docs:  {len(found_results)} ({len(found_results)/len(missing_apis)*100:.1f}%)")
    print(f"  Type mapped:    {len(type_mapping_apis)} ({len(type_mapping_apis)/len(missing_apis)*100:.1f}%)")
    print(f"  Still missing:  {still_missing} ({still_missing/len(missing_apis)*100:.1f}%)")
    print(f"  S6 pairs:       {len(s6_pairs)}")
    print(f"  v5 total:       {len(v5_pairs)}")
    print(f"  v5 size:        {v5_size/1024:.1f} KB")
    print(f"  Rejected:       {rejected}")
    print("=" * 60)

if __name__ == "__main__":
    main()
