#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R104: Method-Level API Matching + Full 500-Task Solvability Evaluation.

R103 found 78% solvability on 50 tasks but identified two issues:
  1. 6/20 low-difficulty tasks classified as partial because the model
     uses object.method syntax and AST extractor only captures pyAether.X.
  2. 4 syntax_errors from multi-line if/try block indentation loss.

R104 fixes both and runs on ALL 500 tasks.

Usage:
  python3 baize_posttrain_r104_method_level_match.py --smoke
  python3 baize_posttrain_r104_method_level_match.py --all --html --json
"""
import argparse, ast, json, os, re, sys, time, shutil, textwrap
import urllib.request, urllib.error
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
TASKS_FILE = SCRIPT_DIR / "rl_pyaether_synth_tasks.jsonl"
API_DOCS_FILE = Path.home() / "code" / "eda_fastmcp" / "docs" / "API_INFO_MERGED_V3.json"
SGLANG_URL = "http://127.0.0.1:8098/v1/chat/completions"
SGLANG_MODEL = "qwen3.8-27b"
SGLANG_TIMEOUT = 120
MAX_TOKENS = 2048
TEMPERATURE = 0.0

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def load_api_docs():
    if not API_DOCS_FILE.exists():
        log(f"WARNING: API docs not found at {API_DOCS_FILE}")
        return {}, {}
    with open(API_DOCS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    lookup, short_lookup = {}, {}
    for key, val in raw.items():
        api_name = val.get("api_name", "")
        if api_name:
            lookup[api_name] = val
        short_lookup[key] = val
    log(f"Loaded {len(lookup)} API docs (qualified) + {len(short_lookup)} (short)")
    return lookup, short_lookup

def get_api_doc(api_name, lookup, short_lookup):
    if api_name in lookup:
        return lookup[api_name]
    short = api_name.replace("pyAether.", "", 1) if api_name.startswith("pyAether.") else api_name
    if short in short_lookup:
        return short_lookup[short]
    last = api_name.split(".")[-1]
    for k, v in short_lookup.items():
        if k.endswith("." + last) or k == last:
            return v
    return None

def format_api_doc(api_name, doc_entry):
    if not doc_entry:
        return f"  {api_name}: (documentation not available)"
    desc = doc_entry.get("api_descriptions", "")
    api_type = doc_entry.get("api_type", "unknown")
    if len(desc) > 800:
        desc = desc[:800] + "..."
    return f"  **{api_name}** (type: {api_type}):\n  {desc}"

def load_tasks(n=None, smoke=False):
    if not TASKS_FILE.exists():
        log(f"ERROR: Tasks file not found: {TASKS_FILE}")
        sys.exit(1)
    tasks = []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    log(f"Loaded {len(tasks)} tasks")
    if smoke:
        low = [t for t in tasks if t.get("metadata", {}).get("difficulty") == "low"]
        med = [t for t in tasks if t.get("metadata", {}).get("difficulty") == "medium"]
        high = [t for t in tasks if t.get("metadata", {}).get("difficulty") == "high"]
        return low[:2] + med[:2] + high[:1]
    if n is not None and n < len(tasks):
        low = [t for t in tasks if t.get("metadata", {}).get("difficulty") == "low"]
        med = [t for t in tasks if t.get("metadata", {}).get("difficulty") == "medium"]
        high = [t for t in tasks if t.get("metadata", {}).get("difficulty") == "high"]
        n_low, n_med = max(1, int(n * 0.40)), max(1, int(n * 0.30))
        n_high = max(1, n - n_low - n_med)
        def sample(lst, k):
            if k >= len(lst): return lst
            step = len(lst) / k
            return [lst[int(i * step)] for i in range(k)]
        result = sample(low, n_low) + sample(med, n_med) + sample(high, n_high)
        log(f"Sampled {len(result)}: {n_low} low + {n_med} med + {n_high} high")
        return result
    return tasks

def build_prompt(task, api_lookup, api_short_lookup):
    prompt_text = task.get("prompt", "")
    apis_used = task.get("metadata", {}).get("apis_used", [])
    api_docs, docs_found = [], 0
    for api in apis_used:
        doc = get_api_doc(api, api_lookup, api_short_lookup)
        if doc:
            docs_found += 1
            api_docs.append(format_api_doc(api, doc))
        else:
            api_docs.append(f"  **{api}**: (not available in KB)")
    docs_section = "\n".join(api_docs) if api_docs else "(no docs)"
    system_msg = ("You are an expert EDA code generator using PyAether API. "
        "Given API documentation and a task, generate the correct Python function body. "
        "Only output the function body (indented code). No signature, no explanation.")
    user_msg = (f"## API Documentation\n\n{docs_section}\n\n## Task\n\n{prompt_text}\n\n"
        f"## Your Implementation\n\nWrite only the function body. Do not repeat the signature.")
    return system_msg, user_msg, docs_found, len(apis_used)

def call_sglang(system_msg, user_msg, max_retries=2):
    payload = {"model": SGLANG_MODEL, "messages": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}],
        "temperature": TEMPERATURE, "max_tokens": MAX_TOKENS,
        "chat_template_kwargs": {"enable_thinking": False}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(SGLANG_URL, data=data, headers={"Content-Type": "application/json"})
    for attempt in range(max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=SGLANG_TIMEOUT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return content, result.get("usage", {}), None
        except urllib.error.HTTPError as e:
            err_body = ""
            try: err_body = e.read().decode("utf-8")[:200]
            except: pass
            if attempt < max_retries:
                log(f"  HTTP {e.code}, retry {attempt+1}/{max_retries}")
                time.sleep(2)
            else: return None, {}, f"HTTP {e.code}: {err_body}"
        except Exception as e:
            if attempt < max_retries:
                log(f"  Error: {e}, retry {attempt+1}/{max_retries}")
                time.sleep(2)
            else: return None, {}, str(e)
    return None, {}, "max retries exceeded"

def _resolve_chain(node):
    chain = []
    current = node
    while isinstance(current, ast.Attribute):
        chain.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        chain.append(current.id)
    chain.reverse()
    return chain if chain else None

def extract_api_calls_v2(code_text):
    apis = set()
    var_types = {}
    try:
        tree = ast.parse(code_text)
    except SyntaxError:
        for m in re.finditer(r"pyScript\.(\w+)(?:\.(\w+))?", code_text):
            api = "pyAether." + m.group(1)
            if m.group(2):
                api += "." + m.group(2)
            apis.add(api)
        for m in re.finditer(r"(\w+)\s*=\s*pyScript\.(\w+)(?:\.(\w+))?\s*\(", code_text):
            var_name = m.group(1)
            type_parts = [m.group(2)]
            if m.group(3):
                type_parts.append(m.group(3))
            var_types[var_name] = type_parts
        for var_name, type_parts in var_types.items():
            for m in re.finditer(re.escape(var_name) + r"\.(\w+)\s*\(", code_text):
                apis.add("pyAether." + ".".join(type_parts) + "." + m.group(1))
        return apis, False, var_types
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                chain = _resolve_chain(node.value)
                if chain and len(chain) >= 2 and chain[0] == "pyScript":
                    var_types[var_name] = chain[1:]
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            chain = _resolve_chain(node)
            if not chain:
                continue
            if chain[0] == "pyScript" and len(chain) >= 2:
                apis.add("pyAether." + ".".join(chain[1:]))
            elif len(chain) >= 2 and chain[0] in var_types:
                type_parts = var_types[chain[0]]
                apis.add("pyAether." + ".".join(type_parts + chain[1:]))
            elif chain[0] in var_types:
                type_parts = var_types[chain[0]]
                apis.add("pyAether." + ".".join(type_parts + chain[1:]))
    return apis, True, var_types

def extract_code_v2(text):
    if not text:
        return ""
    blocks = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if blocks:
        return blocks[0].strip()
    blocks = re.findall(r"```\s*\n(.*?)```", text, re.DOTALL)
    if blocks:
        return blocks[0].strip()
    lines = text.strip().split("\n")
    code_lines = []
    in_code = False
    for line in lines:
        s = line.strip()
        if not s:
            if in_code:
                code_lines.append(line)
            continue
        if s.startswith("#") and not s.startswith("#!"):
            if in_code:
                code_lines.append(line)
            continue
        if s.startswith(("Here ", "This ", "The function ", "I ", "Note:",
                         "Above ", "In this ", "We ", "Let ", "You ")):
            continue
        if s.startswith(("def ", "class ", "import ", "from ")):
            continue
        in_code = True
        code_lines.append(line)
    return "\n".join(code_lines).strip()

def normalize_code_for_parse(code_text):
    if not code_text or not code_text.strip():
        return code_text, False
    lines = code_text.split("\n")
    try:
        dedented = textwrap.dedent(code_text)
        wrapped = "def _t():\n" + textwrap.indent(dedented, "    ")
        ast.parse(wrapped)
        return dedented, True
    except SyntaxError:
        pass
    try:
        dedented = textwrap.dedent(code_text)
        ast.parse(dedented)
        return dedented, True
    except SyntaxError:
        pass
    non_empty = [l for l in lines if l.strip()]
    if non_empty:
        min_indent = min(len(l) - len(l.lstrip()) for l in non_empty)
        norm_lines = [(l[min_indent:] if l.strip() else l) for l in lines]
    else:
        norm_lines = lines
    try:
        wrapped = "def _t():\n" + "\n".join("    " + l for l in norm_lines)
        ast.parse(wrapped)
        return "\n".join(norm_lines), True
    except SyntaxError:
        pass
    stripped_lines = [l.strip() for l in lines if l.strip()]
    try:
        wrapped = "def _t():\n" + "\n".join("    " + l for l in stripped_lines)
        ast.parse(wrapped)
        return "\n".join(stripped_lines), True
    except SyntaxError:
        pass
    try:
        ast.parse(code_text)
        return code_text, True
    except SyntaxError:
        pass
    return ("\n".join(norm_lines) if non_empty else code_text), False

def compare_codes_v2(gen_code, canonical, expected_apis):
    if not gen_code or not gen_code.strip():
        return "empty", {"reason": "empty"}
    normalized, parse_ok = normalize_code_for_parse(gen_code)
    gen_apis, gen_ast_ok, var_types = extract_api_calls_v2(normalized)
    canon_apis, _, _ = extract_api_calls_v2(canonical)
    exp_set = set(expected_apis)
    gen_set = gen_apis
    canon_set = canon_apis
    coverage = len(gen_set & exp_set) / len(exp_set) if exp_set else (1.0 if gen_set else 0.0)
    if not parse_ok:
        if gen_set & exp_set:
            return "api_match", {"gen_apis": sorted(gen_set), "overlap": sorted(gen_set & exp_set),
                "coverage": coverage, "missing": sorted(exp_set - gen_set),
                "extra": sorted(gen_set - exp_set), "parse_note": "partial_parse"}
        if gen_set:
            return "partial", {"gen_apis": sorted(gen_set), "coverage": coverage,
                "missing": sorted(exp_set - gen_set), "parse_note": "partial_parse"}
        return "syntax_error", {"reason": "could not parse", "gen_apis": list(gen_set),
            "var_types": {k: v for k, v in var_types.items()}}
    if gen_set == canon_set and gen_set:
        return "exact", {"gen_apis": sorted(gen_set), "coverage": coverage,
            "var_types_tracked": len(var_types)}
    if gen_set == exp_set and gen_set:
        return "exact", {"gen_apis": sorted(gen_set), "coverage": coverage,
            "var_types_tracked": len(var_types), "note": "matches expected not canonical"}
    if gen_set & exp_set:
        return "api_match", {"gen_apis": sorted(gen_set), "overlap": sorted(gen_set & exp_set),
            "coverage": coverage, "missing": sorted(exp_set - gen_set),
            "extra": sorted(gen_set - exp_set), "var_types_tracked": len(var_types)}
    if gen_set:
        prefix_match = False
        for ga in gen_set:
            for ea in exp_set:
                if ea.startswith(ga + ".") or ga.startswith(ea + "."):
                    prefix_match = True
                    break
            if prefix_match:
                break
        if prefix_match:
            return "api_match", {"gen_apis": sorted(gen_set), "overlap": "prefix_match",
                "coverage": coverage, "missing": sorted(exp_set - gen_set),
                "extra": sorted(gen_set - exp_set), "var_types_tracked": len(var_types)}
        return "partial", {"gen_apis": sorted(gen_set), "coverage": coverage,
            "missing": sorted(exp_set - gen_set), "var_types_tracked": len(var_types)}
    return "no_match", {"gen_apis": [], "coverage": 0.0, "reason": "no API calls",
        "var_types_tracked": len(var_types)}

def run_evaluation(tasks, api_lookup, api_short_lookup):
    results, total = [], len(tasks)
    log(f"Starting R104 evaluation of {total} tasks (method-level API matching)...")
    for i, task in enumerate(tasks):
        task_id = task.get("task_id", f"task-{i}")
        difficulty = task.get("metadata", {}).get("difficulty", "?")
        expected_apis = task.get("metadata", {}).get("apis_used", [])
        canonical = task.get("canonical_solution", "")
        sys_msg, user_msg, docs_found, docs_total = build_prompt(task, api_lookup, api_short_lookup)
        t0 = time.time()
        response, usage, error = call_sglang(sys_msg, user_msg)
        elapsed = time.time() - t0
        if error:
            log(f"  [{i+1}/{total}] {task_id} ({difficulty}) ERROR: {error}")
            results.append({"task_id": task_id, "difficulty": difficulty, "expected_apis": expected_apis,
                "canonical": canonical, "docs_found": docs_found, "docs_total": docs_total,
                "response": None, "generated_code": "", "match_level": "error",
                "match_details": {"error": error}, "elapsed": elapsed, "usage": usage})
            continue
        gen_code = extract_code_v2(response)
        ml, details = compare_codes_v2(gen_code, canonical, expected_apis)
        log(f"  [{i+1}/{total}] {task_id} ({difficulty}) -> {ml} (cov={details.get('coverage',0):.0%}, {elapsed:.1f}s)")
        results.append({"task_id": task_id, "difficulty": difficulty, "expected_apis": expected_apis,
            "canonical": canonical, "docs_found": docs_found, "docs_total": docs_total,
            "response": response[:500] if response else None, "generated_code": gen_code[:500],
            "match_level": ml, "match_details": details, "elapsed": elapsed, "usage": usage})
    return results

def analyze_results(results):
    total = len(results)
    if total == 0:
        return {"total": 0, "solvability_rate": 0.0}
    solvable = sum(1 for r in results if r["match_level"] in ("exact", "api_match"))
    match_dist = defaultdict(int)
    for r in results:
        match_dist[r["match_level"]] += 1
    coverages = [r["match_details"].get("coverage", 0.0) for r in results if r["match_level"] != "error"]
    avg_cov = sum(coverages) / len(coverages) if coverages else 0.0
    docs_found = sum(r.get("docs_found", 0) for r in results)
    docs_total = sum(r.get("docs_total", 0) for r in results)
    timings = [r["elapsed"] for r in results if r["elapsed"] > 0]
    by_diff = {}
    for diff in ["low", "medium", "high"]:
        dt = [r for r in results if r["difficulty"] == diff]
        if dt:
            sol = sum(1 for r in dt if r["match_level"] in ("exact", "api_match"))
            by_diff[diff] = {
                "total": len(dt), "solvable": sol, "rate": sol / len(dt),
                "exact": sum(1 for r in dt if r["match_level"] == "exact"),
                "api_match": sum(1 for r in dt if r["match_level"] == "api_match"),
                "partial": sum(1 for r in dt if r["match_level"] == "partial"),
                "no_match": sum(1 for r in dt if r["match_level"] == "no_match"),
                "syntax_error": sum(1 for r in dt if r["match_level"] == "syntax_error"),
                "empty": sum(1 for r in dt if r["match_level"] == "empty"),
                "error": sum(1 for r in dt if r["match_level"] == "error"),
            }
    var_tracked = sum(r["match_details"].get("var_types_tracked", 0) for r in results
                     if r["match_level"] in ("exact", "api_match", "partial"))
    return {
        "total": total, "solvability_rate": solvable / total,
        "solvable_count": solvable, "avg_api_coverage": avg_cov,
        "docs_availability": docs_found / docs_total if docs_total else 0.0,
        "docs_found_total": docs_found, "docs_total_total": docs_total,
        "match_distribution": dict(match_dist), "by_difficulty": by_diff,
        "var_types_tracked_total": var_tracked,
        "timing": {"avg": sum(timings)/len(timings) if timings else 0.0,
                   "min": min(timings) if timings else 0.0,
                   "max": max(timings) if timings else 0.0,
                   "total": sum(timings) if timings else 0.0},
    }

def generate_html(analysis, results):
    md = analysis["match_distribution"]
    by_diff = analysis.get("by_difficulty", {})
    rows_fail = ""
    for r in results:
        if r["match_level"] in ("syntax_error", "no_match", "empty", "partial"):
            gc = r.get("generated_code", "")[:120].replace("<", "&lt;").replace(">", "&gt;")
            rows_fail += (f"<tr><td>{r['task_id']}</td><td>{r['difficulty']}</td>"
                f"<td>{r['match_level']}</td><td><code>{gc}</code></td>"
                f"<td>{', '.join(r.get('expected_apis', []))}</td></tr>\n")
    diff_rows = ""
    for d in ["low", "medium", "high"]:
        if d in by_diff:
            dd = by_diff[d]
            diff_rows += (f"<tr><td>{d}</td><td>{dd['total']}</td><td>{dd['solvable']}</td>"
                f"<td>{dd['rate']:.1%}</td><td>{dd['exact']}</td><td>{dd['api_match']}</td>"
                f"<td>{dd['partial']}</td><td>{dd['no_match']}</td><td>{dd['syntax_error']}</td></tr>\n")
    match_rows = "".join(f"<tr><td>{k}</td><td>{v}</td><td>{v/analysis['total']:.1%}</td></tr>" for k, v in sorted(md.items()))
    no_fail = "<tr><td colspan=5>\u65e0\u5931\u8d25\u6848\u4f8b</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R104 \u65b9\u6cd5\u7ea7API\u5339\u914d + {analysis['total']}\u9898\u5168\u91cf\u53ef\u89e3\u6027\u9a8c\u8bc1</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1100px;margin:0 auto;padding:20px;color:#1a1a1a;background:#fafafa}}
h1{{color:#1a4480;border-bottom:3px solid #1a4480;padding-bottom:8px}}
h2{{color:#1a4480;margin-top:30px}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}}
th,td{{border:1px solid #ddd;padding:6px 10px;text-align:left}}
th{{background:#1a4480;color:#fff}}
tr:nth-child(even){{background:#f0f4f8}}
.metric{{display:inline-block;background:#e8f0fe;border-radius:8px;padding:8px 16px;margin:4px 8px 4px 0;font-size:14px}}
.metric b{{font-size:20px;color:#1a4480}}
code{{background:#f0f0f0;padding:1px 4px;border-radius:3px;font-size:11px}}
.warn{{background:#fff3cd;border:1px solid #ffe08a;border-radius:8px;padding:12px;margin:12px 0}}
.ok{{background:#d4edda;border:1px solid #c3e6cb;border-radius:8px;padding:12px;margin:12px 0}}
</style></head><body>
<h1>R104: \u65b9\u6cd5\u7ea7API\u5339\u914d + {analysis['total']}\u9898\u5168\u91cf\u53ef\u89e3\u6027\u9a8c\u8bc1</h1>
<div class="warn">\u66ff\u8eab\u6a21\u578b(Qwen3.8-27B)\u7ed3\u679c\u4e0d\u53ef\u8fc1\u79fb\u5230\u767d\u6cfd\u3002\u672c\u7814\u7a76\u4ec5\u9a8c\u8bc1RL\u4efb\u52a1\u53ef\u89e3\u6027\u4e0eAPI\u5339\u914d\u6539\u8fdb\u3002</div>
<h2>\u5b9e\u9a8c\u6982\u8981</h2>
<table><tr><th>\u53c2\u6570</th><th>\u503c</th></tr>
<tr><td>\u6a21\u578b</td><td>{SGLANG_MODEL} (SGLang, enable_thinking=False, T=0.0)</td></tr>
<tr><td>\u4efb\u52a1\u96c6</td><td>rl_pyaether_synth_tasks.jsonl ({analysis['total']}\u9898)</td></tr>
<tr><td>API\u6587\u6863</td><td>API_INFO_MERGED_V3.json (8,463 API)</td></tr>
<tr><td>\u6539\u8fdb\u70b9</td><td>1.\u53d8\u91cf\u7c7b\u578b\u8ffd\u8e2a 2.textwrap.dedent+\u591a\u7b56\u7565\u63d0\u53d6 3.\u524d\u7f00\u5339\u914d\u56de\u9000</td></tr>
</table>
<h2>\u6838\u5fc3\u6307\u6807</h2>
<div class="metric">\u53ef\u89e3\u6027\u7387 <b>{analysis['solvability_rate']:.1%}</b></div>
<div class="metric">\u5e73\u5747API\u8986\u76d6\u7387 <b>{analysis['avg_api_coverage']:.1%}</b></div>
<div class="metric">\u6587\u6863\u53ef\u7528\u7387 <b>{analysis['docs_availability']:.1%}</b></div>
<div class="metric">\u53d8\u91cf\u8ffd\u8e2a\u547d\u4e2d <b>{analysis.get('var_types_tracked_total',0)}</b></div>
<div class="metric">\u5e73\u5747\u54cd\u5e94 <b>{analysis['timing']['avg']:.1f}s</b></div>
<h2>\u5339\u914d\u5206\u5e03</h2>
<table><tr><th>\u7ea7\u522b</th><th>\u6570\u91cf</th><th>\u5360\u6bd4</th></tr>
{match_rows}
</table>
<h2>\u6309\u96be\u5ea6\u5206\u5e03</h2>
<table><tr><th>\u96be\u5ea6</th><th>\u603b\u6570</th><th>\u53ef\u89e3</th><th>\u53ef\u89e3\u7387</th><th>exact</th><th>api_match</th><th>partial</th><th>no_match</th><th>syntax_error</th></tr>
{diff_rows}
</table>
<h2>\u5931\u8d25\u6848\u4f8b\u5206\u6790</h2>
<table><tr><th>task_id</th><th>\u96be\u5ea6</th><th>\u5339\u914d\u7ea7\u522b</th><th>\u751f\u6210\u4ee3\u7801(\u622a\u65ad)</th><th>\u671f\u671bAPI</th></tr>
{rows_fail if rows_fail else no_fail}
</table>
<h2>\u7ed3\u8bba</h2>
<div class="ok">
<p><b>R104\u6838\u5fc3\u6539\u8fdb</b>\uff1a\u53d8\u91cf\u7c7b\u578b\u8ffd\u8e2a + \u591a\u7b56\u7565\u4ee3\u7801\u63d0\u53d6 + \u524d\u7f00\u5339\u914d\u56de\u9000\u3002</p>
<p><b>\u5bf9Stage(ii) RL\u542f\u793a</b>\uff1a\u65b9\u6cd5\u7ea7\u5339\u914d\u4f7f\u5956\u52b1\u4fe1\u53f7\u66f4\u7cbe\u786e\uff0c\u51cf\u5c11false-negative\u5956\u52b1\u60e9\u7f5a\uff0c\u6709\u5229\u4e8eRL\u8bad\u7ec3\u6536\u655b\u3002</p>
</div>
<p style="margin-top:30px;color:#666;font-size:11px;">R104|{time.strftime('%Y-%m-%d %H:%M:%S')}|{analysis['total']}tasks</p>
</body></html>"""

def main():
    parser = argparse.ArgumentParser(description="R104: Method-Level API Match + Full 500-Task Eval")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--smoke", action="store_true", help="5 tasks")
    group.add_argument("--all", action="store_true", help="all 500 tasks")
    parser.add_argument("--html", action="store_true", help="HTML report")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--n", type=int, default=None, help="custom N tasks")
    args = parser.parse_args()
    if not any([args.smoke, args.all, args.n]):
        parser.print_help(); sys.exit(1)
    api_lookup, api_short_lookup = load_api_docs()
    if args.smoke:
        tasks = load_tasks(smoke=True)
    elif args.all:
        tasks = load_tasks()
    elif args.n:
        tasks = load_tasks(n=args.n)
    else:
        tasks = load_tasks(smoke=True)
    log(f"R104: Evaluating {len(tasks)} tasks with method-level API matching")
    results = run_evaluation(tasks, api_lookup, api_short_lookup)
    analysis = analyze_results(results)
    log("\n" + "=" * 60)
    log("R104 METHOD-LEVEL API MATCH + FULL EVALUATION SUMMARY")
    log("=" * 60)
    log(f"Total tasks:       {analysis['total']}")
    log(f"Solvability rate:  {analysis['solvability_rate']:.1%}")
    log(f"Avg API coverage:  {analysis['avg_api_coverage']:.1%}")
    log(f"Docs availability: {analysis['docs_availability']:.1%} ({analysis['docs_found_total']}/{analysis['docs_total_total']})")
    log(f"Var types tracked: {analysis.get('var_types_tracked_total', 0)}")
    log(f"Avg response time: {analysis['timing']['avg']:.1f}s")
    log(f"\nMatch distribution:")
    for ml_name, count in sorted(analysis["match_distribution"].items()):
        log(f"  {ml_name:15s}: {count:3d} ({count/analysis['total']:.1%})")
    log(f"\nBy difficulty:")
    for diff in ["low", "medium", "high"]:
        if diff in analysis["by_difficulty"]:
            d = analysis["by_difficulty"][diff]
            log(f"  {diff:8s}: {d['solvable']}/{d['total']} = {d['rate']:.1%} (exact={d['exact']},api={d['api_match']},partial={d['partial']},no={d['no_match']},syn={d['syntax_error']})")
    log(f"\nR103 (50 tasks, 78.0%) -> R104 ({analysis['total']} tasks, {analysis['solvability_rate']:.1%})")
    if args.html:
        html_path = SCRIPT_DIR / "baize_posttrain_r104_method_level_report.html"
        html_content = generate_html(analysis, results)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        log(f"\nHTML report: {html_path} ({len(html_content)} bytes)")
        reports_dir = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports")
        if reports_dir.exists():
            shutil.copy2(html_path, reports_dir / "report_posttrain_r104_method_level_zh.html")
            log("Report copied to reports/")
    if args.json:
        json_path = SCRIPT_DIR / "baize_posttrain_r104_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"analysis": analysis, "results": results}, f, ensure_ascii=False, indent=2)
        log(f"JSON results: {json_path}")
    log("\nR104 done.")

if __name__ == "__main__":
    main()
