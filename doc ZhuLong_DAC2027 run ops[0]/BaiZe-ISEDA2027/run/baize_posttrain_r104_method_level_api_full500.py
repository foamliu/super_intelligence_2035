#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R104: Method-Level API Resolution + Full 500-Task Solvability Evaluation.

⚠️ Surrogate results are NOT transferable to BaiZe.
R103 found low-difficulty 65% (vs med/high 86.7%) due to object.method extraction
limitation: when model writes `obj = pyScript.X.Y(); obj.method()`, the method call
on `obj` was NOT recognized as a pyAether API call.

R104 fixes this with:
  1. Variable tracking: build symbol table var → pyAether.X.Y from assignments
  2. Method-level resolution: resolve var.method() → pyAether.X.Y.method
  3. Method-name fallback: if full path doesn't match, match by suffix
  4. Full 500-task evaluation (vs R103's 50-task sample)
  5. Task filtering recommendations for RL training

Usage:
  python3 baize_posttrain_r104_method_level_api_full500.py --smoke
  python3 baize_posttrain_r104_method_level_api_full500.py --n50 --html
  python3 baize_posttrain_r104_method_level_api_full500.py --all --html --json
"""
import argparse, ast, json, os, re, sys, time, shutil
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

# ── API docs loading ─────────────────────────────────────────────────

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

# ── Task loading ─────────────────────────────────────────────────────

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

# ── Prompt building ──────────────────────────────────────────────────

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

# ── SGLang call ──────────────────────────────────────────────────────

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

# ── Code extraction ──────────────────────────────────────────────────

def extract_code_from_response(text):
    if not text: return ""
    blocks = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if blocks: return blocks[0].strip()
    blocks = re.findall(r"```\s*\n(.*?)```", text, re.DOTALL)
    if blocks: return blocks[0].strip()
    lines = text.strip().split("\n")
    code_lines = []
    for line in lines:
        s = line.strip()
        if not s or (s.startswith("#") and not s.startswith("#!")):
            code_lines.append(line); continue
        if s.startswith(("Here", "This ", "The ", "I ", "Note:", "Above")):
            continue
        code_lines.append(line)
    return "\n".join(code_lines).strip()

# ── R104 KEY: Method-level API extraction with var tracking ──────────

def _extract_pyscript_chain(node):
    """Extract pyAether.X.Y path from an AST node if it's a pyScript chain."""
    if isinstance(node, ast.Call):
        return _extract_pyscript_chain(node.func)
    if isinstance(node, ast.Attribute):
        chain, current = [], node
        while isinstance(current, ast.Attribute):
            chain.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            chain.append(current.id)
        chain.reverse()
        if chain and chain[0] == "pyScript":
            return "pyAether." + ".".join(chain[1:])
    return None

def extract_api_calls_v2(code_text):
    """Extract pyAether API calls with variable tracking.
    Returns (set_of_api_paths, parse_ok, resolved_via_var_count).
    """
    apis = set()
    var_resolved = 0
    try:
        tree = ast.parse(code_text)
    except SyntaxError:
        for m in re.finditer(r"pyScript\.(\w+)(?:\.(\w+))?", code_text):
            apis.add("pyAether." + m.group(1) + (f".{m.group(2)}" if m.group(2) else ""))
        return apis, False, 0
    # Phase 1: Build var symbol table
    var_table = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            rhs_api = _extract_pyscript_chain(node.value)
            if rhs_api:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_table[target.id] = rhs_api
    # Phase 2: Walk AST for all API calls
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            chain, current = [], node
            while isinstance(current, ast.Attribute):
                chain.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                chain.append(current.id)
            chain.reverse()
            if chain and chain[0] == "pyScript":
                apis.add("pyAether." + ".".join(chain[1:]))
            elif chain and chain[0] in var_table:
                base = var_table[chain[0]]
                if len(chain) > 1:
                    apis.add(base + "." + ".".join(chain[1:]))
                else:
                    apis.add(base)
                var_resolved += 1
    # Phase 3: Call on var from pyScript
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in var_table:
                apis.add(var_table[node.func.id])
                var_resolved += 1
    return apis, True, var_resolved

def extract_api_calls_simple(code_text):
    """Simple extraction without var tracking (R103 method, for comparison)."""
    apis = set()
    try:
        tree = ast.parse(code_text)
    except SyntaxError:
        for m in re.finditer(r"pyScript\.(\w+)(?:\.(\w+))?", code_text):
            apis.add("pyAether." + m.group(1) + (f".{m.group(2)}" if m.group(2) else ""))
        return apis, False
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            chain, current = [], node
            while isinstance(current, ast.Attribute):
                chain.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                chain.append(current.id)
            chain.reverse()
            if chain and chain[0] == "pyScript":
                apis.add("pyAether." + ".".join(chain[1:]))
    return apis, True

def compare_codes_v2(gen_code, canonical, expected_apis):
    """R104 enhanced comparison with method-level matching and var tracking."""
    if not gen_code or not gen_code.strip():
        return "empty", {"reason": "empty"}
    lines = gen_code.split("\n")
    parse_ok = False
    norm_code = gen_code
    # Strategy 1: dedent + wrap
    non_empty = [l for l in lines if l.strip()]
    if non_empty:
        min_indent = min(len(l) - len(l.lstrip()) for l in non_empty)
        norm_lines = [(l[min_indent:] if l.strip() else l) for l in lines]
    else:
        norm_lines = lines
    try:
        ast.parse("def _t():\n" + "\n".join("    " + l for l in norm_lines))
        parse_ok = True
        norm_code = "\n".join(norm_lines)
    except SyntaxError:
        pass
    # Strategy 2: strip + flatten
    if not parse_ok:
        stripped_lines = [l.strip() for l in lines if l.strip()]
        try:
            ast.parse("def _t():\n" + "\n".join("    " + l for l in stripped_lines))
            parse_ok = True
            norm_code = "\n".join(stripped_lines)
        except SyntaxError as e:
            return "syntax_error", {"reason": str(e), "gen_apis": []}
    # R104: Extract with var tracking + simple for comparison
    gen_apis, _, var_resolved = extract_api_calls_v2(norm_code)
    gen_apis_simple, _ = extract_api_calls_simple(norm_code)
    canon_apis, _ = extract_api_calls_simple(canonical)
    exp_set = set(expected_apis)
    gen_set = gen_apis
    gen_set_simple = gen_apis_simple
    coverage = len(gen_set & exp_set) / len(exp_set) if exp_set else (1.0 if gen_set else 0.0)
    coverage_simple = len(gen_set_simple & exp_set) / len(exp_set) if exp_set else (1.0 if gen_set_simple else 0.0)
    exp_methods = {api.split(".")[-1] for api in exp_set}
    gen_methods = {api.split(".")[-1] for api in gen_set}
    method_name_overlap = gen_methods & exp_methods
    details = {
        "gen_apis": sorted(gen_set),
        "gen_apis_simple": sorted(gen_set_simple),
        "var_resolved_count": var_resolved,
        "coverage": coverage,
        "coverage_simple": coverage_simple,
        "coverage_improved": coverage > coverage_simple,
        "method_name_overlap": sorted(method_name_overlap),
    }
    if gen_set == canon_apis and gen_set:
        return "exact", details
    if gen_set & exp_set:
        details["overlap"] = sorted(gen_set & exp_set)
        details["missing"] = sorted(exp_set - gen_set)
        details["extra"] = sorted(gen_set - exp_set)
        return "api_match", details
    if method_name_overlap and not (gen_set & exp_set):
        details["matched_methods"] = sorted(method_name_overlap)
        details["missing"] = sorted(exp_set - gen_set)
        return "method_match", details
    if gen_set:
        details["missing"] = sorted(exp_set - gen_set)
        return "partial", details
    return "no_match", {"gen_apis": [], "coverage": 0.0, "reason": "no API calls",
                        "var_resolved_count": var_resolved}

# ── Evaluation runner ────────────────────────────────────────────────

def run_evaluation(tasks, api_lookup, api_short_lookup):
    results, total = [], len(tasks)
    log(f"Starting R104 evaluation of {total} tasks...")
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
        gen_code = extract_code_from_response(response)
        ml, details = compare_codes_v2(gen_code, canonical, expected_apis)
        cov = details.get("coverage", 0)
        vr = details.get("var_resolved_count", 0)
        log(f"  [{i+1}/{total}] {task_id} ({difficulty}) -> {ml} (cov={cov:.0%}, vr={vr}, {elapsed:.1f}s)")
        results.append({"task_id": task_id, "difficulty": difficulty, "expected_apis": expected_apis,
            "canonical": canonical, "docs_found": docs_found, "docs_total": docs_total,
            "response": response[:500] if response else None, "generated_code": gen_code[:500],
            "match_level": ml, "match_details": details, "elapsed": elapsed, "usage": usage})
    return results

# ── Analysis ─────────────────────────────────────────────────────────

def analyze_results(results):
    total = len(results)
    by_diff = defaultdict(lambda: defaultdict(int))
    by_match = defaultdict(int)
    failure_modes, api_cov, elapsed_times = [], [], []
    var_resolved_total = 0
    coverage_improved_count = 0
    for r in results:
        diff, ml = r["difficulty"], r["match_level"]
        by_diff[diff]["total"] += 1
        by_diff[diff][ml] += 1
        by_match[ml] += 1
        api_cov.append(r["match_details"].get("coverage", 0.0))
        elapsed_times.append(r["elapsed"])
        vr = r["match_details"].get("var_resolved_count", 0)
        var_resolved_total += vr
        if r["match_details"].get("coverage_improved", False):
            coverage_improved_count += 1
        if ml in ("syntax_error", "no_match", "empty", "error", "partial"):
            failure_modes.append({"task_id": r["task_id"], "difficulty": diff, "match_level": ml,
                "reason": r["match_details"].get("reason", r["match_details"].get("error", "")),
                "expected_apis": r["expected_apis"],
                "generated_code": r["generated_code"][:200] if r["generated_code"] else ""})
    solvable_strict = by_match.get("exact", 0) + by_match.get("api_match", 0)
    solvable_extended = solvable_strict + by_match.get("method_match", 0)
    diff_sol = {}
    for diff, counts in by_diff.items():
        t = counts["total"]
        s_strict = counts.get("exact", 0) + counts.get("api_match", 0)
        s_ext = s_strict + counts.get("method_match", 0)
        diff_sol[diff] = {"total": t, "solvable_strict": s_strict, "solvable_extended": s_ext,
            "rate_strict": s_strict/t if t else 0, "rate_extended": s_ext/t if t else 0,
            "exact": counts.get("exact",0), "api_match": counts.get("api_match",0),
            "method_match": counts.get("method_match",0), "partial": counts.get("partial",0),
            "no_match": counts.get("no_match",0), "syntax_error": counts.get("syntax_error",0),
            "empty": counts.get("empty",0), "error": counts.get("error",0)}
    docs_found = sum(r["docs_found"] for r in results)
    docs_total = sum(r["docs_total"] for r in results)
    keep_tasks, drop_tasks, review_tasks = [], [], []
    for r in results:
        ml = r["match_level"]
        if ml in ("exact", "api_match"): keep_tasks.append(r["task_id"])
        elif ml == "method_match": review_tasks.append(r["task_id"])
        else: drop_tasks.append(r["task_id"])
    return {"total": total,
        "solvability_rate_strict": solvable_strict/total if total else 0,
        "solvability_rate_extended": solvable_extended/total if total else 0,
        "match_distribution": dict(by_match), "by_difficulty": diff_sol,
        "avg_api_coverage": sum(api_cov)/len(api_cov) if api_cov else 0,
        "full_coverage_count": sum(1 for c in api_cov if c >= 1.0),
        "zero_coverage_count": sum(1 for c in api_cov if c == 0.0),
        "docs_availability": docs_found/docs_total if docs_total else 0,
        "docs_found_total": docs_found, "docs_total_total": docs_total,
        "timing": {"avg": sum(elapsed_times)/len(elapsed_times) if elapsed_times else 0,
            "min": min(elapsed_times) if elapsed_times else 0,
            "max": max(elapsed_times) if elapsed_times else 0,
            "total": sum(elapsed_times)},
        "var_resolved_total": var_resolved_total,
        "coverage_improved_count": coverage_improved_count,
        "method_match_count": by_match.get("method_match", 0),
        "failure_modes": failure_modes[:20],
        "task_filtering": {"keep": len(keep_tasks), "review": len(review_tasks),
            "drop": len(drop_tasks), "keep_ids": keep_tasks[:50],
            "drop_ids": drop_tasks[:50], "review_ids": review_tasks[:30]}}

# ── HTML report ──────────────────────────────────────────────────────

def generate_html(analysis, results):
    total = analysis["total"]
    sol_s = analysis["solvability_rate_strict"]
    sol_e = analysis["solvability_rate_extended"]
    avg_cov = analysis["avg_api_coverage"]
    docs = analysis["docs_availability"]
    vr = analysis["var_resolved_total"]
    ci = analysis["coverage_improved_count"]
    mm = analysis["method_match_count"]
    diff_rows = ""
    for diff in ["low", "medium", "high"]:
        if diff in analysis["by_difficulty"]:
            d = analysis["by_difficulty"][diff]
            diff_rows += (f"<tr><td>{diff}</td><td>{d['total']}</td>"
                f"<td>{d['solvable_strict']} ({d['rate_strict']:.1%})</td>"
                f"<td>{d['solvable_extended']} ({d['rate_extended']:.1%})</td>"
                f"<td>{d['exact']}</td><td>{d['api_match']}</td>"
                f"<td>{d['method_match']}</td><td>{d['partial']}</td>"
                f"<td>{d['no_match']}</td><td>{d['syntax_error']}</td></tr>")
    match_bars = ""
    colors = {"exact": "#28a745", "api_match": "#20c997", "method_match": "#17a2b8",
              "partial": "#ffc107", "no_match": "#fd7e14", "syntax_error": "#dc3545",
              "empty": "#6c757d", "error": "#343a40"}
    for ml, count in sorted(analysis["match_distribution"].items(), key=lambda x: -x[1]):
        pct = count / total * 100 if total else 0
        color = colors.get(ml, "#6c757d")
        match_bars += (f'<div style="margin:4px 0;"><span style="display:inline-block;width:100px;'
            f'font-size:12px;">{ml}</span><span style="display:inline-block;width:40px;text-align:right;'
            f'font-size:12px;">{count}</span><span style="background:{color};display:inline-block;'
            f'height:16px;width:{pct*3:.0f}px;margin-left:4px;border-radius:3px;"></span>'
            f'<span style="margin-left:4px;font-size:11px;">{pct:.1f}%</span></div>')
    frows = ""
    for fm in analysis["failure_modes"][:15]:
        gc = fm.get("generated_code", "")[:120].replace("<", "&lt;").replace(" >", "&gt;")
        frows += (f"<tr><td>{fm['task_id']}</td><td>{fm['difficulty']}</td><td>{fm['match_level']}</td>"
            f"<td>{fm.get('reason','')[:80]}</td><td><code>{', '.join(fm.get('expected_apis',[]))[:60]}</code></td>"
            f"<td><pre style=\"font-size:10px;\">{gc}</pre></td></tr>")
    tf = analysis["task_filtering"]
    sol_msg = ("绝大多数合成题在提供文档后可被强模型解决——奖励信号有效。" if sol_s > 0.5
        else "部分题目即使有文档也难以解决——需检查题目质量。")
    vr_msg = (f"变量追踪解析了 {vr} 个方法调用，{ci} 个任务的覆盖率因此提升——"
        f"R103的partial问题已部分修复。" if ci > 0 else
        "本次评测中变量追踪未提升覆盖率——模型可能直接使用pyScript链式调用。")
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>R104 方法级API解析+全量评测</title>
<style>body{{font-family:sans-serif;max-width:960px;margin:0 auto;padding:20px;background:#f8f9fa;}}
h1{{color:#1a1a2e;border-bottom:3px solid #0f3460;padding-bottom:10px;}}h2{{color:#16213e;margin-top:25px;}}
table{{border-collapse:collapse;width:100%;margin:8px 0;background:white;}}th,td{{border:1px solid #dee2e6;padding:6px;font-size:13px;}}
th{{background:#0f3460;color:white;}}.metric{{display:inline-block;background:#e9ecef;border-radius:8px;padding:10px;margin:4px;text-align:center;}}
.metric-value{{font-size:24px;font-weight:bold;color:#0f3460;}}.metric-label{{font-size:11px;color:#666;}}
.warning{{background:#fff3cd;border-left:4px solid #ffc107;padding:8px;margin:8px 0;}}.success{{background:#d4edda;border-left:4px solid #28a745;padding:8px;margin:8px 0;}}
.info{{background:#d1ecf1;border-left:4px solid #17a2b8;padding:8px;margin:8px 0;}}
code{{background:#e9ecef;padding:1px 3px;border-radius:3px;font-size:11px;}}pre{{background:#f1f3f5;padding:6px;border-radius:4px;overflow-x:auto;}}</style></head><body>
<h1>R104: 方法级API解析 + 全量500题可解性评测</h1>
<div class="warning"><b>⚠️ 替身模型结果不可迁移到白泽。</b> 使用Qwen3.8-27B验证。27B ≠ 2B BaiZe。</div>
<h2>1. 摘要</h2><div>
<div class="metric"><div class="metric-value">{total}</div><div class="metric-label">评测题数</div></div>
<div class="metric"><div class="metric-value">{sol_s:.1%}</div><div class="metric-label">可解率(严格)</div></div>
<div class="metric"><div class="metric-value">{sol_e:.1%}</div><div class="metric-label">可解率(扩展)</div></div>
<div class="metric"><div class="metric-value">{avg_cov:.1%}</div><div class="metric-label">API覆盖率</div></div>
<div class="metric"><div class="metric-value">{docs:.1%}</div><div class="metric-label">文档可用率</div></div>
<div class="metric"><div class="metric-value">{analysis['timing']['avg']:.1f}s</div><div class="metric-label">平均响应</div></div></div>
<h2>2. R104改进点：方法级API解析</h2>
<div class="info"><ul>
<li>变量追踪：构建符号表 var→pyAether.X.Y，解析 var.method() 为 pyAether.X.Y.method</li>
<li>本次评测中变量追踪解析了 <b>{vr}</b> 个方法调用</li>
<li>{ci} 个任务的API覆盖率因此提升</li>
<li>方法名级匹配(method_match)新增 <b>{mm}</b> 个任务：方法名匹配但完整路径不匹配</li>
<li>{vr_msg}</li>
</ul></div>
<h2>3. 与R103对比（50题→500题）</h2>
<table><tr><th>指标</th><th>R103(50题)</th><th>R104(500题,严格)</th><th>R104(500题,扩展)</th></tr>
<tr><td>可解率</td><td>78.0%</td><td>{sol_s:.1%}</td><td>{sol_e:.1%}</td></tr>
<tr><td>API覆盖率</td><td>76.7%</td><td>{avg_cov:.1%}</td><td>—</td></tr>
<tr><td>评测题数</td><td>50</td><td>{total}</td><td>{total}</td></tr></table>
<h2>4. 按难度分层</h2>
<table><tr><th>难度</th><th>题数</th><th>可解(严格)</th><th>可解(扩展)</th><th>Exact</th><th>API</th><th>Method</th><th>Partial</th><th>NoMatch</th><th>SynErr</th></tr>{diff_rows}</table>
<h2>5. 匹配分布</h2>{match_bars}
<h2>6. 失败模式（前15）</h2>
<table><tr><th>Task</th><th>难度</th><th>级别</th><th>原因</th><th>API</th><th>生成代码</th></tr>{frows}</table>
<h2>7. RL训练任务过滤建议</h2>
<div class="success"><ul>
<li><b>保留(keep)</b>: {tf['keep']} 题 — exact或api_match，奖励信号明确</li>
<li><b>复审(review)</b>: {tf['review']} 题 — method_match，方法名对但路径不对，需人工确认</li>
<li><b>丢弃(drop)</b>: {tf['drop']} 题 — partial/no_match/syntax_error/empty，奖励信号弱</li>
<li>建议：RL训练使用keep集；review集做pass@8 profiling后决定；drop集从训练中移除</li>
</ul></div>
<h2>8. RL奖励设计启示</h2>
<ul>
<li>严格可解率{sol_s:.1%}: 绝大多数题有明确奖励信号 → GRPO可行</li>
<li>扩展可解率{sol_e:.1%}（含方法名匹配）: 考虑R2分档奖励——方法名匹配给部分分</li>
<li>文档可用率{docs:.1%}: rollout时注入API文档是标准配置</li>
<li>语法错误{analysis['match_distribution'].get('syntax_error',0)}题: 需在reward中扣分（R3臂）</li>
</ul>
<h2>9. 参数</h2>
<table><tr><th>参数</th><th>值</th></tr>
<tr><td>模型</td><td>{SGLANG_MODEL}</td></tr><tr><td>温度</td><td>{TEMPERATURE}</td></tr><tr><td>max_tokens</td><td>{MAX_TOKENS}</td></tr>
<tr><td>enable_thinking</td><td>False</td></tr>
<tr><td>API提取</td><td>R104 v2（变量追踪+方法名匹配）</td></tr>
<tr><td>评测题数</td><td>{total}（全量）</td></tr></table>
<p style="margin-top:30px;color:#666;font-size:11px;">R104|{time.strftime('%Y-%m-%d %H:%M:%S')}|⚠️替身不可迁移</p></body></html>"""
    return html

# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="R104: Method-Level API Resolution + Full 500-Task Evaluation")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--smoke", action="store_true", help="5 tasks quick test")
    group.add_argument("--n50", action="store_true", help="50 tasks stratified")
    group.add_argument("--all", action="store_true", help="all 500 tasks")
    parser.add_argument("--html", action="store_true", help="generate HTML report")
    parser.add_argument("--json", action="store_true", help="output JSON results")
    parser.add_argument("--n", type=int, default=None, help="custom N tasks")
    args = parser.parse_args()
    if not any([args.smoke, args.n50, args.all, args.n]):
        parser.print_help(); sys.exit(1)
    api_lookup, api_short_lookup = load_api_docs()
    if args.smoke: tasks = load_tasks(smoke=True)
    elif args.n50: tasks = load_tasks(n=50)
    elif args.all: tasks = load_tasks()
    elif args.n: tasks = load_tasks(n=args.n)
    else: tasks = load_tasks(smoke=True)
    log(f"R104: Evaluating {len(tasks)} tasks with method-level API resolution")
    results = run_evaluation(tasks, api_lookup, api_short_lookup)
    analysis = analyze_results(results)
    log("\n" + "=" * 60)
    log("R104 METHOD-LEVEL API RESOLUTION + FULL EVALUATION SUMMARY")
    log("=" * 60)
    log(f"Total tasks:           {analysis['total']}")
    log(f"Solvability (strict):  {analysis['solvability_rate_strict']:.1%}")
    log(f"Solvability (extended):{analysis['solvability_rate_extended']:.1%}")
    log(f"Avg API coverage:      {analysis['avg_api_coverage']:.1%}")
    log(f"Docs availability:     {analysis['docs_availability']:.1%}")
    log(f"Var-resolved calls:    {analysis['var_resolved_total']}")
    log(f"Coverage improved:     {analysis['coverage_improved_count']} tasks")
    log(f"Method-name matches:   {analysis['method_match_count']} tasks")
    log(f"\nMatch distribution:")
    for ml, count in sorted(analysis["match_distribution"].items(), key=lambda x: -x[1]):
        log(f"  {ml:15s}: {count:3d} ({count/analysis['total']:.1%})")
    log(f"\nBy difficulty (strict / extended):")
    for diff in ["low", "medium", "high"]:
        if diff in analysis["by_difficulty"]:
            d = analysis["by_difficulty"][diff]
            log(f"  {diff:8s}: {d['solvable_strict']}/{d['total']} = {d['rate_strict']:.1%} (strict) / "
                f"{d['solvable_extended']}/{d['total']} = {d['rate_extended']:.1%} (extended)")
    tf = analysis["task_filtering"]
    log(f"\nTask filtering: keep={tf['keep']}, review={tf['review']}, drop={tf['drop']}")
    log(f"\nTiming: avg={analysis['timing']['avg']:.1f}s, total={analysis['timing']['total']:.1f}s")
    if args.html:
        html_path = SCRIPT_DIR / "baize_posttrain_r104_report.html"
        html_content = generate_html(analysis, results)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        log(f"\nHTML report: {html_path} ({len(html_content)} bytes)")
        reports_dir = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports")
        if reports_dir.exists():
            shutil.copy2(html_path, reports_dir / "report_posttrain_r104_method_level_full500_zh.html")
            log(f"Report copied to reports/")
    if args.json:
        json_path = SCRIPT_DIR / "baize_posttrain_r104_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"analysis": analysis, "results": results}, f, ensure_ascii=False, indent=2)
        log(f"JSON results: {json_path}")
    log("\nR104 done.")

if __name__ == "__main__":
    main()
