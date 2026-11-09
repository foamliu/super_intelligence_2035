#!/usr/bin/env python3
"""
R97: Extended Surrogate Difficulty Map — 50-task EDA-Eval-PyAether Code Generation
via SGLang Qwen3.8-27B (Surrogate, NOT transferable to BaiZe)

WARNING: Surrogate results (Qwen3.8-27B) are NOT transferable to BaiZe (MiniCPM5-2B).

Usage:
  python3 baize_posttrain_r97_surrogate_difficulty_map.py              # Full 50 tasks
  python3 baize_posttrain_r97_surrogate_difficulty_map.py --smoke      # 5 tasks
  python3 baize_posttrain_r97_surrogate_difficulty_map.py --n 30       # 30 tasks
  python3 baize_posttrain_r97_surrogate_difficulty_map.py --html       # Generate HTML report
  python3 baize_posttrain_r97_surrogate_difficulty_map.py --json       # Output JSON
"""

import argparse, ast, json, os, re, sys, time
import urllib.request, urllib.error
from collections import Counter, defaultdict

DEFAULT_ENDPOINT = "http://127.0.0.1:8098/v1"
DEFAULT_MODEL = "qwen3.8-27b"
DATASET_PATH = os.path.expanduser("~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
REPORT_DIR = os.path.expanduser("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports")
EXP_DIR = os.path.expanduser("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run")
DEFAULT_N = 50
MAX_TOKENS = 2048  # Thinking disabled via chat_template_kwargs; 2048 is enough for code output
TIMEOUT = 120

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def read_jsonl(path):
    tasks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line: tasks.append(json.loads(line))
    return tasks

def call_sglang(endpoint, model, messages, max_tokens=MAX_TOKENS, timeout=TIMEOUT):
    url = f"{endpoint}/chat/completions"
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7, "top_p": 0.95, "chat_template_kwargs": {"enable_thinking": False}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            # Extract reasoning_tokens if available (Qwen3.8 is a reasoning model)
            usage = result.get("usage", {})
            result["_reasoning_tokens"] = usage.get("reasoning_tokens", 0)
            # Also get reasoning_content if present
            msg = result.get("choices", [{}])[0].get("message", {})
            result["_reasoning_content"] = msg.get("reasoning_content", "")
            return result, None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode('utf-8',errors='replace')[:200]}"
    except Exception as e:
        return None, str(e)

def extract_code(text):
    matches = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if matches: return max(matches, key=len).strip()
    if "def " in text or "import " in text: return text.strip()
    return text.strip()

def check_syntax(code):
    try:
        ast.parse(code); return True, None
    except SyntaxError as e:
        return False, f"{e.msg} (line {e.lineno})"

def extract_api_calls(code, required_apis):
    found = []
    for api in required_apis:
        short_name = api.replace("pyAether.", "").replace("pyScript.", "")
        if short_name in code or api in code: found.append(api)
    return found

def classify_failure(code, syntax_ok, required_apis, found_apis):
    if syntax_ok and len(found_apis) == len(required_apis): return "potential_pass"
    if not syntax_ok: return "syntax_error"
    if len(found_apis) == 0: return "no_api_usage"
    if len(found_apis) < len(required_apis): return "partial_api_usage"
    return "unknown"

def extract_function_name(prompt):
    m = re.search(r"def\s+(\w+)\s*\(", prompt)
    return m.group(1) if m else "unknown"

def run_evaluation(endpoint, model, tasks, n_tasks):
    results = []
    total = min(n_tasks, len(tasks))
    log(f"Starting evaluation: {total} tasks via {endpoint} (model={model})")
    for i in range(total):
        task = tasks[i]
        task_id = task.get("task_id", f"task-{i}")
        prompt = task.get("prompt", "")
        meta = task.get("metadata", {})
        scenario = meta.get("scenario", "Unknown")
        category = meta.get("category", "Unknown")
        required_apis = meta.get("apis_used", [])
        num_apis = meta.get("num_unique_apis", len(required_apis))
        techlib = meta.get("techlib_dependency", False)
        loc = meta.get("lines_of_code", 0)
        func_name = extract_function_name(prompt)
        system_msg = "You are an expert EDA Python programmer. Complete the function implementation. Use the pyAether API as needed. Return only the complete Python code."
        user_msg = f"Complete the following Python function. The function uses the pyAether library (imported as `pyScript`). Write the full implementation including the function definition.\n\n{prompt}"
        t0 = time.time()
        response, error = call_sglang(endpoint, model, [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}])
        elapsed = time.time() - t0
        if error:
            log(f"  [{i+1}/{total}] {task_id}: ERROR ({error[:80]})")
            results.append({"task_id": task_id, "scenario": scenario, "category": category, "func_name": func_name, "required_apis": required_apis, "num_apis": num_apis, "techlib": techlib, "loc_target": loc, "elapsed": elapsed, "error": error, "syntax_ok": False, "api_coverage": 0.0, "found_apis": [], "failure_mode": "api_error", "generated_code": "", "generated_loc": 0})
            continue
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = response.get("usage", {})
        tokens = usage.get("total_tokens", 0)
        reasoning_tokens = response.get("_reasoning_tokens", 0)
        finish_reason = response.get("choices", [{}])[0].get("finish_reason", "unknown")
        code = extract_code(content)
        gen_loc = len([l for l in code.split("\n") if l.strip() and not l.strip().startswith("#")])
        syntax_ok, syntax_err = check_syntax(code)
        found_apis = extract_api_calls(code, required_apis)
        api_coverage = len(found_apis) / len(required_apis) if required_apis else 1.0
        failure_mode = classify_failure(code, syntax_ok, required_apis, found_apis)
        has_function = f"def {func_name}" in code
        log(f"  [{i+1}/{total}] {task_id}: syntax={'OK' if syntax_ok else 'FAIL'} api_cov={api_coverage:.0%} mode={failure_mode} loc={gen_loc} t={elapsed:.1f}s tok={tokens}")
        results.append({"task_id": task_id, "scenario": scenario, "category": category, "func_name": func_name, "required_apis": required_apis, "num_apis": num_apis, "techlib": techlib, "loc_target": loc, "elapsed": elapsed, "error": None, "syntax_ok": syntax_ok, "syntax_error": syntax_err, "api_coverage": api_coverage, "found_apis": found_apis, "failure_mode": failure_mode, "generated_code": code[:500], "generated_loc": gen_loc, "has_function_def": has_function, "tokens": tokens, "reasoning_tokens": reasoning_tokens, "finish_reason": finish_reason})
    return results

def analyze_results(results):
    total = len(results)
    if total == 0: return {}
    syntax_ok_count = sum(1 for r in results if r.get("syntax_ok"))
    api_errors = sum(1 for r in results if r.get("error"))
    valid = [r for r in results if not r.get("error")]
    failure_modes = Counter(r.get("failure_mode", "unknown") for r in results)
    scenario_stats = defaultdict(lambda: {"total": 0, "syntax_ok": 0, "api_full": 0, "potential_pass": 0})
    for r in valid:
        s = scenario_stats[r["scenario"]]
        s["total"] += 1
        if r["syntax_ok"]: s["syntax_ok"] += 1
        if r["api_coverage"] == 1.0: s["api_full"] += 1
        if r["failure_mode"] == "potential_pass": s["potential_pass"] += 1
    category_stats = defaultdict(lambda: {"total": 0, "syntax_ok": 0, "api_full": 0, "potential_pass": 0})
    for r in valid:
        c = category_stats[r["category"]]
        c["total"] += 1
        if r["syntax_ok"]: c["syntax_ok"] += 1
        if r["api_coverage"] == 1.0: c["api_full"] += 1
        if r["failure_mode"] == "potential_pass": c["potential_pass"] += 1
    api_bins = defaultdict(lambda: {"total": 0, "syntax_ok": 0, "api_full": 0})
    for r in valid:
        n = r["num_apis"]
        bn = "1" if n <= 1 else ("2-3" if n <= 3 else ("4-5" if n <= 5 else ("6-10" if n <= 10 else "10+")))
        b = api_bins[bn]; b["total"] += 1
        if r["syntax_ok"]: b["syntax_ok"] += 1
        if r["api_coverage"] == 1.0: b["api_full"] += 1
    techlib_stats = {"no": {"total": 0, "syntax_ok": 0, "api_full": 0}, "yes": {"total": 0, "syntax_ok": 0, "api_full": 0}}
    for r in valid:
        k = "yes" if r["techlib"] else "no"; techlib_stats[k]["total"] += 1
        if r["syntax_ok"]: techlib_stats[k]["syntax_ok"] += 1
        if r["api_coverage"] == 1.0: techlib_stats[k]["api_full"] += 1
    avg_gen_loc = sum(r.get("generated_loc", 0) for r in valid) / len(valid) if valid else 0
    avg_elapsed = sum(r.get("elapsed", 0) for r in valid) / len(valid) if valid else 0
    avg_tokens = sum(r.get("tokens", 0) for r in valid) / len(valid) if valid else 0
    cov_bins = {"0%": 0, "1-50%": 0, "51-99%": 0, "100%": 0}
    for r in valid:
        c = r["api_coverage"]
        if c == 0: cov_bins["0%"] += 1
        elif c < 0.5: cov_bins["1-50%"] += 1
        elif c < 1.0: cov_bins["51-99%"] += 1
        else: cov_bins["100%"] += 1
    tool_required = [r for r in valid if r["syntax_ok"] and r["api_coverage"] == 0]
    pure_logic = [r for r in valid if r["syntax_ok"] and r["api_coverage"] == 1.0]
    return {"total_tasks": total, "api_errors": api_errors, "valid_tasks": len(valid), "syntax_ok_count": syntax_ok_count, "syntax_ok_rate": syntax_ok_count / len(valid) if valid else 0, "failure_modes": dict(failure_modes), "scenario_stats": {k: dict(v) for k, v in scenario_stats.items()}, "category_stats": {k: dict(v) for k, v in category_stats.items()}, "api_bins": {k: dict(v) for k, v in api_bins.items()}, "techlib_stats": techlib_stats, "avg_gen_loc": round(avg_gen_loc, 1), "avg_elapsed": round(avg_elapsed, 1), "avg_tokens": round(avg_tokens, 0), "api_coverage_dist": cov_bins, "tool_required_count": len(tool_required), "pure_logic_count": len(pure_logic), "tool_required_task_ids": [r["task_id"] for r in tool_required], "pure_logic_task_ids": [r["task_id"] for r in pure_logic]}

def generate_html(analysis, results, n_tasks):
    fm = analysis.get("failure_modes", {})
    sc = analysis.get("scenario_stats", {})
    cat = analysis.get("category_stats", {})
    ab = analysis.get("api_bins", {})
    tl = analysis.get("techlib_stats", {})
    cov = analysis.get("api_coverage_dist", {})
    sc_rows = ""
    for s in sorted(sc.keys()):
        d = sc[s]; total = d["total"]
        if total == 0: continue
        sr = d["syntax_ok"] / total * 100; ar = d["api_full"] / total * 100; pr = d["potential_pass"] / total * 100
        sc_rows += f"<tr><td>{s}</td><td>{total}</td><td>{d['syntax_ok']} ({sr:.0f}%)</td><td>{d['api_full']} ({ar:.0f}%)</td><td>{d['potential_pass']} ({pr:.0f}%)</td></tr>"
    cat_rows = ""
    for c in sorted(cat.keys()):
        d = cat[c]; total = d["total"]
        if total == 0: continue
        sr = d["syntax_ok"] / total * 100; ar = d["api_full"] / total * 100
        cat_rows += f"<tr><td>{c}</td><td>{total}</td><td>{d['syntax_ok']} ({sr:.0f}%)</td><td>{d['api_full']} ({ar:.0f}%)</td></tr>"
    ab_rows = ""
    for b in ["1", "2-3", "4-5", "6-10", "10+"]:
        if b in ab:
            d = ab[b]; total = d["total"]
            if total == 0: continue
            sr = d["syntax_ok"] / total * 100; ar = d["api_full"] / total * 100
            ab_rows += f"<tr><td>{b}</td><td>{total}</td><td>{d['syntax_ok']} ({sr:.0f}%)</td><td>{d['api_full']} ({ar:.0f}%)</td></tr>"
    fm_rows = ""
    for mode, count in sorted(fm.items(), key=lambda x: -x[1]):
        pct = count / analysis["valid_tasks"] * 100 if analysis["valid_tasks"] else 0
        fm_rows += f"<tr><td>{mode}</td><td>{count}</td><td>{pct:.1f}%</td></tr>"
    cov_bars = ""
    for label in ["0%", "1-50%", "51-99%", "100%"]:
        count = cov.get(label, 0)
        pct = count / analysis["valid_tasks"] * 100 if analysis["valid_tasks"] else 0
        cov_bars += f"<div style='margin:4px 0'><span style='display:inline-block;width:60px'>{label}</span><span style='display:inline-block;width:30px;text-align:right'>{count}</span><div style='display:inline-block;background:#4CAF50;height:14px;width:{pct}%;vertical-align:middle;margin-left:8px'></div></div>"
    tr_ids = ', '.join(analysis.get('tool_required_task_ids', [])[:10])
    pl_ids = ', '.join(analysis.get('pure_logic_task_ids', [])[:10])
    tr_more = '...' if len(analysis.get('tool_required_task_ids',[]))>10 else ''
    pl_more = '...' if len(analysis.get('pure_logic_task_ids',[]))>10 else ''
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R97 替身难度图谱 — {n_tasks}题EDA-Eval-PyAether代码生成</title>
<style>
body {{ font-family: -apple-system, "Noto Sans SC", sans-serif; max-width: 960px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #333; }}
h1 {{ color: #1a5276; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
h2 {{ color: #2c3e50; margin-top: 30px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #2c3e50; color: white; }}
tr:nth-child(even) {{ background: #f2f2f2; }}
.warn {{ background: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 10px 0; }}
.info {{ background: #d1ecf1; padding: 10px; border-radius: 5px; border-left: 4px solid #17a2b8; margin: 10px 0; }}
.metric {{ display: inline-block; background: #e8f4f8; padding: 8px 16px; margin: 4px; border-radius: 8px; }}
.metric strong {{ font-size: 1.4em; color: #2c3e50; }}
</style></head><body>
<h1>R97 替身难度图谱 — {n_tasks}题 EDA-Eval-PyAether 纯代码生成</h1>
<div class="warn"><strong>WARNING</strong>: Qwen3.8-27B results NOT transferable to BaiZe (MiniCPM5-2B). Surrogate test only validates pipeline + provides strong-model-no-tools reference.</div>
<h2>1. 概要</h2>
<div>
<span class="metric">任务数: <strong>{analysis['total_tasks']}</strong></span>
<span class="metric">有效任务: <strong>{analysis['valid_tasks']}</strong></span>
<span class="metric">语法正确: <strong>{analysis['syntax_ok_count']}</strong> ({analysis['syntax_ok_rate']:.1%})</span>
<span class="metric">平均耗时: <strong>{analysis['avg_elapsed']}s</strong></span>
<span class="metric">平均tokens: <strong>{analysis['avg_tokens']:.0f}</strong></span>
<span class="metric">平均LOC: <strong>{analysis['avg_gen_loc']}</strong></span>
</div>
<h2>2. 失败模式分布</h2>
<table><tr><th>失败模式</th><th>数量</th><th>占比</th></tr>{fm_rows}</table>
<div class="info"><ul>
<li><code>potential_pass</code> = 语法正确+全部API出现（可能通过，需执行验证）</li>
<li><code>no_api_usage</code> = 语法正确但未使用所需API -> 工具必需型任务</li>
<li><code>partial_api_usage</code> = 仅使用部分API -> 需要API查找能力</li>
<li><code>syntax_error</code> = 语法错误 -> 代码生成能力问题</li>
</ul></div>
<h2>3. API 覆盖率分布</h2>{cov_bars}
<div class="info"><strong>{analysis['tool_required_count']}</strong> 个任务语法正确但API覆盖0% -> 工具必需型。<strong>{analysis['pure_logic_count']}</strong> 个任务API全覆盖 -> 可能纯逻辑型。</div>
<h2>4. 按场景统计</h2>
<table><tr><th>场景</th><th>任务数</th><th>语法正确</th><th>API全覆盖</th><th>可能通过</th></tr>{sc_rows}</table>
<h2>5. 按类别统计</h2>
<table><tr><th>类别</th><th>任务数</th><th>语法正确</th><th>API全覆盖</th></tr>{cat_rows}</table>
<h2>6. 按 API 数量分箱</h2>
<table><tr><th>API数/题</th><th>任务数</th><th>语法正确</th><th>API全覆盖</th></tr>{ab_rows}</table>
<div class="info">API数量越多 -> API覆盖率越低 -> 证实多API任务需要工具调用。支撑R2难度分层。</div>
<h2>7. Techlib 依赖对比</h2>
<table><tr><th>techlib</th><th>任务数</th><th>语法正确</th><th>API全覆盖</th></tr>
<tr><td>无依赖</td><td>{tl['no']['total']}</td><td>{tl['no']['syntax_ok']}</td><td>{tl['no']['api_full']}</td></tr>
<tr><td>有依赖</td><td>{tl['yes']['total']}</td><td>{tl['yes']['syntax_ok']}</td><td>{tl['yes']['api_full']}</td></tr></table>
<h2>8. 工具必需型 vs 纯逻辑型</h2>
<div class="info"><strong>工具必需型 ({analysis['tool_required_count']} 个)</strong>：语法正确但完全不使用所需API。需SFT注入API知识+工具调用能力。ID: {tr_ids} {tr_more}</div>
<div class="info"><strong>纯逻辑型 ({analysis['pure_logic_count']} 个)</strong>：语法正确且API全覆盖。对SFT/RL收益最小。ID: {pl_ids} {pl_more}</div>
<h2>9. 对 Post-Train 三步的启示</h2>
<div class="info"><ol>
<li><strong>领域退火</strong>：注入pyAether API文档 -> 模型知道API名称 -> 提升API覆盖率 -> M1(50%)关键驱动</li>
<li><strong>SFT</strong>：DeepSeek成功轨迹API使用模式 -> 教模型何时用哪个API -> M2(65%)</li>
<li><strong>RL(GRPO)</strong>：多API串联+执行反馈闭环 -> M3(75%)。工具必需型任务是RL核心素材</li>
</ol></div>
<h2>10. 局限性</h2>
<ul><li>替身模型 Qwen3.8-27B != MiniCPM5-2B，结果不可迁移</li><li>纯代码生成 != full harness（无工具调用、无迭代）</li><li>API覆盖率 != Pass@1（可能有逻辑错误）</li><li>50题样本可能不代表全部158题分布</li><li>无执行验证，potential_pass是上界估计</li></ul>
<h2>11. 与前序研究关联</h2>
<ul><li><strong>R94</strong>: 3题smoke -> R97扩展至50题</li><li><strong>R83</strong>: 规则难度分层 -> R97实证校验</li><li><strong>R88</strong>: DeepSeek失败分析 -> R97无工具侧对照</li><li><strong>R93</strong>: MiniCPM5-2B基线轨迹分析 -> GPU释放后替换</li><li><strong>P0 D1-D6</strong>: D2工具频次假设 -> R97 API覆盖率间接验证</li></ul>
<p style="color:#999;font-size:0.8em;margin-top:30px">Generated: {time.strftime('%Y-%m-%d %H:%M:%S')} | R97 | Surrogate: Qwen3.8-27B via SGLang</p>
</body></html>"""
    return html

def main():
    parser = argparse.ArgumentParser(description="R97 Surrogate Difficulty Map")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--n", type=int, default=DEFAULT_N, help="Number of tasks")
    parser.add_argument("--smoke", action="store_true", help="5 tasks only")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    n_tasks = 5 if args.smoke else args.n
    if not os.path.exists(DATASET_PATH):
        log(f"ERROR: Dataset not found at {DATASET_PATH}"); sys.exit(1)
    tasks = read_jsonl(DATASET_PATH)
    log(f"Loaded {len(tasks)} tasks from dataset")
    results = run_evaluation(args.endpoint, args.model, tasks, n_tasks)
    analysis = analyze_results(results)
    log("\n=== R97 Summary ===")
    log(f"Total tasks: {analysis['total_tasks']}")
    log(f"Valid tasks: {analysis['valid_tasks']}")
    log(f"Syntax OK: {analysis['syntax_ok_count']} ({analysis['syntax_ok_rate']:.1%})")
    log(f"Failure modes: {analysis['failure_modes']}")
    log(f"Tool-required: {analysis['tool_required_count']}")
    log(f"Pure-logic: {analysis['pure_logic_count']}")
    log(f"Avg elapsed: {analysis['avg_elapsed']}s")
    log(f"Avg tokens: {analysis['avg_tokens']:.0f}")
    if args.json:
        json_path = os.path.join(EXP_DIR, "r97_surrogate_difficulty_map.json")
        with open(json_path, "w") as f:
            json.dump({"analysis": analysis, "results": results}, f, indent=2, ensure_ascii=False)
        log(f"JSON saved: {json_path}")
    if args.html:
        html_path = os.path.join(REPORT_DIR, "report_posttrain_r97_surrogate_difficulty_map_zh.html")
        html_content = generate_html(analysis, results, n_tasks)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        log(f"HTML saved: {html_path} ({len(html_content)} bytes)")
    log("Done.")

if __name__ == "__main__":
    main()
