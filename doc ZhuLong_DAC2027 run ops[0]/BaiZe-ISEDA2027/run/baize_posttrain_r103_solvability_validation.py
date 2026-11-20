#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R103: Synthetic Task Solvability Validation — Strong-Model with API Documentation.

⚠️ Surrogate results are NOT transferable to BaiZe.
R97 tested Qwen3.8-27B WITHOUT docs → 0% API coverage.
R103 tests WITH docs → quantifies documentation value.
Validates L3: are synthetic tasks solvable?

Usage:
  python3 baize_posttrain_r103_solvability_validation.py --smoke
  python3 baize_posttrain_r103_solvability_validation.py --n50 --html
  python3 baize_posttrain_r103_solvability_validation.py --all --json
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

def extract_api_calls(code_text):
    apis = set()
    try:
        tree = ast.parse(code_text)
    except SyntaxError:
        for m in re.finditer(r"pyScript\.(\w+)(?:\.(\w+))?", code_text):
            apis.add(f"pyAether.{m.group(1)}" + (f".{m.group(2)}" if m.group(2) else ""))
        return apis, False
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            chain, current = [], node
            while isinstance(current, ast.Attribute):
                chain.append(current.attr); current = current.value
            if isinstance(current, ast.Name):
                chain.append(current.id)
            chain.reverse()
            if chain and chain[0] == "pyScript":
                apis.add("pyAether." + ".".join(chain[1:]))
    return apis, True

def compare_codes(gen_code, canonical, expected_apis):
    if not gen_code or not gen_code.strip():
        return "empty", {"reason": "empty"}
    gen_apis, _ = extract_api_calls(gen_code)
    canon_apis, _ = extract_api_calls(canonical)
    # Try multiple strategies to handle mixed indentation from model output
    lines = gen_code.split("\n")
    parse_ok = False
    # Strategy 1: direct wrap with dedent
    non_empty = [l for l in lines if l.strip()]
    if non_empty:
        min_indent = min(len(l) - len(l.lstrip()) for l in non_empty)
        norm_lines = [(l[min_indent:] if l.strip() else l) for l in lines]
    else:
        norm_lines = lines
    try:
        ast.parse("def _t():\n" + "\n".join("    " + l for l in norm_lines))
        parse_ok = True
    except SyntaxError:
        pass
    # Strategy 2: strip all indentation, re-indent uniformly
    if not parse_ok:
        stripped_lines = [l.strip() for l in lines if l.strip()]
        try:
            ast.parse("def _t():\n" + "\n".join("    " + l for l in stripped_lines))
            parse_ok = True
            gen_apis, _ = extract_api_calls("\n".join(stripped_lines))
        except SyntaxError as e:
            return "syntax_error", {"reason": str(e), "gen_apis": list(gen_apis)}
    exp_set, gen_set, canon_set = set(expected_apis), gen_apis, canon_apis
    coverage = len(gen_set & exp_set) / len(exp_set) if exp_set else (1.0 if gen_set else 0.0)
    if gen_set == canon_set and gen_set:
        return "exact", {"gen_apis": sorted(gen_set), "coverage": coverage}
    if gen_set & exp_set:
        return "api_match", {"gen_apis": sorted(gen_set), "overlap": sorted(gen_set & exp_set),
            "coverage": coverage, "missing": sorted(exp_set - gen_set), "extra": sorted(gen_set - exp_set)}
    if gen_set:
        return "partial", {"gen_apis": sorted(gen_set), "coverage": coverage, "missing": sorted(exp_set - gen_set)}
    return "no_match", {"gen_apis": [], "coverage": 0.0, "reason": "no API calls"}

def run_evaluation(tasks, api_lookup, api_short_lookup):
    results, total = [], len(tasks)
    log(f"Starting evaluation of {total} tasks...")
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
        ml, details = compare_codes(gen_code, canonical, expected_apis)
        log(f"  [{i+1}/{total}] {task_id} ({difficulty}) -> {ml} (cov={details.get('coverage',0):.0%}, {elapsed:.1f}s)")
        results.append({"task_id": task_id, "difficulty": difficulty, "expected_apis": expected_apis,
            "canonical": canonical, "docs_found": docs_found, "docs_total": docs_total,
            "response": response[:500] if response else None, "generated_code": gen_code[:500],
            "match_level": ml, "match_details": details, "elapsed": elapsed, "usage": usage})
    return results

def analyze_results(results):
    total = len(results)
    by_diff = defaultdict(lambda: defaultdict(int))
    by_match = defaultdict(int)
    failure_modes, api_cov, elapsed_times = [], [], []
    for r in results:
        diff, ml = r["difficulty"], r["match_level"]
        by_diff[diff]["total"] += 1; by_diff[diff][ml] += 1; by_match[ml] += 1
        api_cov.append(r["match_details"].get("coverage", 0.0))
        elapsed_times.append(r["elapsed"])
        if ml in ("syntax_error", "no_match", "empty", "error", "partial"):
            failure_modes.append({"task_id": r["task_id"], "difficulty": diff, "match_level": ml,
                "reason": r["match_details"].get("reason", r["match_details"].get("error", "")),
                "expected_apis": r["expected_apis"], "generated_code": r["generated_code"][:200]})
    solvable = by_match.get("exact", 0) + by_match.get("api_match", 0)
    diff_sol = {}
    for diff, counts in by_diff.items():
        t = counts["total"]; s = counts.get("exact", 0) + counts.get("api_match", 0)
        diff_sol[diff] = {"total": t, "solvable": s, "rate": s/t if t else 0,
            "exact": counts.get("exact",0), "api_match": counts.get("api_match",0),
            "partial": counts.get("partial",0), "no_match": counts.get("no_match",0),
            "syntax_error": counts.get("syntax_error",0), "empty": counts.get("empty",0),
            "error": counts.get("error",0)}
    docs_found = sum(r["docs_found"] for r in results)
    docs_total = sum(r["docs_total"] for r in results)
    return {"total": total, "solvability_rate": solvable/total if total else 0,
        "match_distribution": dict(by_match), "by_difficulty": diff_sol,
        "avg_api_coverage": sum(api_cov)/len(api_cov) if api_cov else 0,
        "full_coverage_count": sum(1 for c in api_cov if c >= 1.0),
        "zero_coverage_count": sum(1 for c in api_cov if c == 0.0),
        "docs_availability": docs_found/docs_total if docs_total else 0,
        "docs_found_total": docs_found, "docs_total_total": docs_total,
        "timing": {"avg": sum(elapsed_times)/len(elapsed_times) if elapsed_times else 0,
            "min": min(elapsed_times) if elapsed_times else 0,
            "max": max(elapsed_times) if elapsed_times else 0},
        "failure_modes": failure_modes[:20]}

def generate_html(analysis, results):
    total = analysis["total"]; sol = analysis["solvability_rate"]
    avg_cov = analysis["avg_api_coverage"]; docs = analysis["docs_availability"]
    md = analysis["match_distribution"]; bd = analysis["by_difficulty"]
    delta = sol - 0.0
    diff_rows = ""
    for d in ["low", "medium", "high"]:
        if d in bd:
            v = bd[d]
            diff_rows += f"<tr><td>{d}</td><td>{v['total']}</td><td>{v['solvable']}</td><td>{v['rate']:.1%}</td><td>{v['exact']}</td><td>{v['api_match']}</td><td>{v['partial']}</td><td>{v['no_match']}</td><td>{v['syntax_error']}</td></tr>"
    labels = {"exact": "精确匹配", "api_match": "API匹配", "partial": "部分匹配", "no_match": "无匹配", "syntax_error": "语法错误", "empty": "空响应", "error": "错误"}
    colors = {"exact": "#28a745", "api_match": "#20c997", "partial": "#ffc107", "no_match": "#fd7e14", "syntax_error": "#dc3545", "empty": "#6c757d", "error": "#343a40"}
    bars = ""
    for ml, lab in labels.items():
        c = md.get(ml, 0); pct = c/total*100 if total else 0
        bars += f'<div style="margin:4px 0;"><span style="display:inline-block;width:100px;">{lab}</span><span style="display:inline-block;width:36px;text-align:right;">{c}</span><div style="display:inline-block;background:{colors.get(ml,"#999")};height:14px;width:{pct:.1f}%;border-radius:3px;"></div><span style="margin-left:4px;font-size:11px;">{pct:.1f}%</span></div>'
    frows = ""
    for fm in analysis["failure_modes"][:10]:
        gc = fm.get("generated_code", "")[:120].replace("<", "&lt;").replace(">", "&gt;")
        frows += f"<tr><td>{fm['task_id']}</td><td>{fm['difficulty']}</td><td>{fm['match_level']}</td><td>{fm.get('reason','')[:80]}</td><td><code>{', '.join(fm.get('expected_apis',[]))[:60]}</code></td><td><pre style=\"font-size:10px;\">{gc}</pre></td></tr>"
    sol_msg = "绝大多数合成题在提供文档后可被强模型解决——奖励信号有效。" if sol > 0.5 else "部分题目即使有文档也难以解决——需检查题目质量。"
    html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>R103 可解性验证</title>
<style>body{{font-family:sans-serif;max-width:960px;margin:0 auto;padding:20px;background:#f8f9fa;}}
h1{{color:#1a1a2e;border-bottom:3px solid #0f3460;padding-bottom:10px;}}h2{{color:#16213e;margin-top:25px;}}
table{{border-collapse:collapse;width:100%;margin:8px 0;background:white;}}th,td{{border:1px solid #dee2e6;padding:6px;font-size:13px;}}
th{{background:#0f3460;color:white;}}.metric{{display:inline-block;background:#e9ecef;border-radius:8px;padding:10px;margin:4px;text-align:center;}}
.metric-value{{font-size:24px;font-weight:bold;color:#0f3460;}}.metric-label{{font-size:11px;color:#666;}}
.warning{{background:#fff3cd;border-left:4px solid #ffc107;padding:8px;margin:8px 0;}}.success{{background:#d4edda;border-left:4px solid #28a745;padding:8px;margin:8px 0;}}
code{{background:#e9ecef;padding:1px 3px;border-radius:3px;font-size:11px;}}pre{{background:#f1f3f5;padding:6px;border-radius:4px;overflow-x:auto;}}</style></head><body>
<h1>R103: 合成题可解性验证 — 强模型+API文档</h1>
<div class="warning"><b>⚠️ 替身模型结果不可迁移到白泽。</b> 使用Qwen3.8-27B验证合成RL题目在提供API文档后是否可解。27B ≠ 2B BaiZe。</div>
<h2>1. 摘要</h2><div>
<div class="metric"><div class="metric-value">{total}</div><div class="metric-label">评测题数</div></div>
<div class="metric"><div class="metric-value">{sol:.1%}</div><div class="metric-label">可解率</div></div>
<div class="metric"><div class="metric-value">{avg_cov:.1%}</div><div class="metric-label">API覆盖率</div></div>
<div class="metric"><div class="metric-value">{docs:.1%}</div><div class="metric-label">文档可用率</div></div>
<div class="metric"><div class="metric-value">{analysis['timing']['avg']:.1f}s</div><div class="metric-label">平均响应</div></div></div>
<h2>2. 与R97对比</h2><table><tr><th>条件</th><th>API覆盖率</th><th>可解率</th><th>差异</th></tr>
<tr><td>R97无文档</td><td>0%</td><td>0%</td><td>—</td></tr>
<tr><td><b>R103有文档</b></td><td>{avg_cov:.1%}</td><td>{sol:.1%}</td><td><b>+{delta:.1%}</b></td></tr></table>
<h2>3. 按难度分层</h2><table><tr><th>难度</th><th>题数</th><th>可解</th><th>可解率</th><th>Exact</th><th>API</th><th>Partial</th><th>NoMatch</th><th>SynErr</th></tr>{diff_rows}</table>
<h2>4. 匹配分布</h2>{bars}
<h2>5. 失败模式</h2><table><tr><th>Task</th><th>难度</th><th>级别</th><th>原因</th><th>API</th><th>生成代码</th></tr>{frows}</table>
<h2>6. RL训练启示</h2><div class="success"><ul><li>可解率{sol:.1%}:{sol_msg}</li><li>API覆盖率{avg_cov:.1%}:文档→代码路径可行</li><li>文档可用率{docs:.1%}</li><li>R97→R103提升+{delta:.1%}:文档注入是协议可回收主驱动</li></ul></div>
<h2>7. RL奖励建议</h2><ul><li>R2部分分仍推荐:high难度可能偏低</li><li>课程学习:low→medium→high</li><li>文档检索增强:rollout时注入API文档</li><li>有文档仍无法解决的题目应剔除</li></ul>
<h2>8. 参数</h2><table><tr><th>参数</th><th>值</th></tr><tr><td>模型</td><td>{SGLANG_MODEL}</td></tr><tr><td>温度</td><td>{TEMPERATURE}</td></tr><tr><td>max_tokens</td><td>{MAX_TOKENS}</td></tr><tr><td>enable_thinking</td><td>False</td></tr></table>
<p style="margin-top:30px;color:#666;font-size:11px;">R103|{time.strftime('%Y-%m-%d %H:%M:%S')}|⚠️替身不可迁移</p></body></html>"""
    return html

def main():
    parser = argparse.ArgumentParser(description="R103: Solvability Validation with API Docs")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--smoke", action="store_true", help="5 tasks")
    group.add_argument("--n50", action="store_true", help="50 tasks stratified")
    group.add_argument("--all", action="store_true", help="all 500 tasks")
    parser.add_argument("--html", action="store_true", help="HTML report")
    parser.add_argument("--json", action="store_true", help="JSON output")
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
    log(f"R103: Evaluating {len(tasks)} tasks with API doc augmentation")
    results = run_evaluation(tasks, api_lookup, api_short_lookup)
    analysis = analyze_results(results)
    log("\n" + "=" * 60)
    log("R103 SOLVABILITY VALIDATION SUMMARY")
    log("=" * 60)
    log(f"Total tasks:       {analysis['total']}")
    log(f"Solvability rate:  {analysis['solvability_rate']:.1%}")
    log(f"Avg API coverage:  {analysis['avg_api_coverage']:.1%}")
    log(f"Docs availability: {analysis['docs_availability']:.1%} ({analysis['docs_found_total']}/{analysis['docs_total_total']})")
    log(f"Avg response time: {analysis['timing']['avg']:.1f}s")
    log(f"\nMatch distribution:")
    for ml, count in sorted(analysis["match_distribution"].items()):
        log(f"  {ml:15s}: {count:3d} ({count/analysis['total']:.1%})")
    log(f"\nBy difficulty:")
    for diff in ["low", "medium", "high"]:
        if diff in analysis["by_difficulty"]:
            d = analysis["by_difficulty"][diff]
            log(f"  {diff:8s}: {d['solvable']}/{d['total']} = {d['rate']:.1%} (exact={d['exact']},api={d['api_match']},partial={d['partial']},no={d['no_match']},syn={d['syntax_error']})")
    log(f"\nR97 (no docs) -> R103 (with docs) improvement: +{analysis['solvability_rate']:.1%}")
    if args.html:
        html_path = SCRIPT_DIR / "baize_posttrain_r103_solvability_report.html"
        html_content = generate_html(analysis, results)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        log(f"\nHTML report: {html_path} ({len(html_content)} bytes)")
        reports_dir = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports")
        if reports_dir.exists():
            shutil.copy2(html_path, reports_dir / "report_posttrain_r103_solvability_zh.html")
            log(f"Report copied to reports/")
    if args.json:
        json_path = SCRIPT_DIR / "baize_posttrain_r103_solvability_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"analysis": analysis, "results": results}, f, ensure_ascii=False, indent=2)
        log(f"JSON results: {json_path}")
    log("\nR103 done.")

if __name__ == "__main__":
    main()
