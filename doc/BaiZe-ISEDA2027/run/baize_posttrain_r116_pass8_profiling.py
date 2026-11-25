#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R116: Pass@8 Difficulty Profiling — Empirical Validation of Rule-Based Stratification

Surrogate results (Qwen3.8-27B) are NOT transferable to BaiZe (MiniCPM5-2B).
Answers R2 question: pass@8 profiling vs rule-based stratification + discriminability evidence.
"""
import argparse, ast, json, math, os, re, sys, time, random
import urllib.request, urllib.error
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
TASKS_FILE = SCRIPT_DIR / "rl_pyaether_synth_v2.jsonl"
API_DOCS_FILE = Path.home() / "code" / "eda_fastmcp" / "docs" / "API_INFO_MERGED_V3.json"
SGLANG_URL = "http://127.0.0.1:8098/v1/chat/completions"
SGLANG_MODEL = "qwen3.8-27b"
SGLANG_TIMEOUT = 120
MAX_TOKENS = 2048
TEMPERATURE = 0.7
TOP_P = 0.95
N_SAMPLES = 8
CONCURRENCY = 8
DEFAULT_N_PER_TIER = 30
REPORT_DIR = Path("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports")
TIERS = ["L1", "L2", "L3", "L4", "L5"]
NO_DOCS = False  # If True, don't include API docs in prompt (harder condition)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

_api_lookup = {}
_api_short = {}

def load_api_docs():
    global _api_lookup, _api_short
    if not API_DOCS_FILE.exists():
        log(f"WARNING: API docs not found at {API_DOCS_FILE}")
        return
    with open(API_DOCS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    for key, val in raw.items():
        api_name = val.get("api_name", "")
        if api_name:
            _api_lookup[api_name] = val
        _api_short[key] = val
    log(f"Loaded {len(_api_lookup)} API docs (qualified) + {len(_api_short)} (short)")

def get_api_doc(api_name):
    if api_name in _api_lookup:
        return _api_lookup[api_name]
    short = api_name.replace("pyAether.", "", 1) if api_name.startswith("pyAether.") else api_name
    if short in _api_short:
        return _api_short[short]
    last = api_name.split(".")[-1]
    for k, v in _api_short.items():
        if k.endswith("." + last) or k == last:
            return v
    return None

def format_api_doc(api_name):
    doc = get_api_doc(api_name)
    if not doc:
        return f"  {api_name}: (documentation not available)"
    desc = doc.get("api_descriptions", "")
    api_type = doc.get("api_type", "unknown")
    if len(desc) > 600:
        desc = desc[:600] + "..."
    return f"  **{api_name}** (type: {api_type}):\n  {desc}"

def load_tasks():
    tasks = []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    log(f"Loaded {len(tasks)} tasks from {TASKS_FILE.name}")
    return tasks

def sample_by_tier(tasks, n_per_tier, seed=42):
    by_tier = defaultdict(list)
    for t in tasks:
        by_tier[t["metadata"]["difficulty"]].append(t)
    sampled = []
    rng = random.Random(seed)
    for tier in TIERS:
        pool = by_tier.get(tier, [])
        if len(pool) <= n_per_tier:
            sampled.extend(pool)
        else:
            sampled.extend(rng.sample(pool, n_per_tier))
        log(f"  Tier {tier}: {len(pool)} available, sampled {min(n_per_tier, len(pool))}")
    return sampled

def call_sglang(messages, max_tokens=MAX_TOKENS, timeout=SGLANG_TIMEOUT):
    payload = {
        "model": SGLANG_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(SGLANG_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = result.get("usage", {})
            return content, usage.get("completion_tokens", 0), None
    except urllib.error.HTTPError as e:
        return "", 0, f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:200]}"
    except Exception as e:
        return "", 0, str(e)

def build_prompt(task):
    prompt_text = task["prompt"]
    apis = task["metadata"].get("apis_used", [])
    doc_section = ""
    if apis and not NO_DOCS:
        doc_lines = [format_api_doc(a) for a in apis]
        doc_section = "\n\n## API Reference\n" + "\n".join(doc_lines)
    system_msg = "You are an expert EDA Python programmer. Write clean, correct Python code. Only output the Python function, no explanations."
    user_msg = prompt_text + doc_section + "\n\nWrite only the Python function, no markdown formatting."
    return [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]

def extract_code(text):
    if not text:
        return ""
    m = re.search(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    lines = text.strip().split("\n")
    start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("def ") or line.strip().startswith("import "):
            start = i
            break
    return "\n".join(lines[start:]).strip()

def check_syntax(code):
    if not code:
        return False
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def extract_api_calls(code, required_apis):
    found = set()
    if not code:
        return found
    for api in required_apis:
        short = api.replace("pyAether.", "", 1) if api.startswith("pyAether.") else api
        aliases = [api, short, f"pyScript.{short}", f"pyAether.{short}"]
        for alias in aliases:
            if alias in code:
                found.add(api)
                break
        if "." + short.split(".")[-1] in code:
            found.add(api)
    return found

def score_completion(code, required_apis):
    syntax_ok = check_syntax(code)
    found_apis = extract_api_calls(code, required_apis)
    api_coverage = len(found_apis) / len(required_apis) if required_apis else 1.0
    passed = syntax_ok and (api_coverage == 1.0)
    return syntax_ok, api_coverage, passed

def pass_at_k(n, c, k):
    if n - c < k:
        return 1.0
    numer = 1.0
    denom = 1.0
    for i in range(k):
        numer *= (n - c - i)
        denom *= (n - i)
    return 1.0 - numer / denom

def evaluate_task(task, n_samples=N_SAMPLES):
    messages = build_prompt(task)
    required_apis = task["metadata"].get("apis_used", [])
    results = []
    t0 = time.time()
    def gen_one(_idx):
        content, tokens, err = call_sglang(messages)
        if err:
            return {"code": "", "tokens": 0, "syntax_ok": False, "api_coverage": 0.0, "passed": False, "error": err}
        code = extract_code(content)
        syntax_ok, api_cov, passed = score_completion(code, required_apis)
        return {"code": code[:500], "tokens": tokens, "syntax_ok": syntax_ok, "api_coverage": api_cov, "passed": passed, "error": None}
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(gen_one, i) for i in range(n_samples)]
        for f in as_completed(futures):
            results.append(f.result())
    elapsed = time.time() - t0
    n_pass = sum(1 for r in results if r["passed"])
    n_syntax = sum(1 for r in results if r["syntax_ok"])
    avg_api_cov = sum(r["api_coverage"] for r in results) / len(results) if results else 0.0
    return {
        "task_id": task["task_id"], "difficulty": task["metadata"]["difficulty"],
        "num_apis": task["metadata"]["num_unique_apis"],
        "assertion_template": task["metadata"].get("assertion_template", ""),
        "n_samples": n_samples, "n_pass": n_pass, "n_syntax_ok": n_syntax,
        "avg_api_coverage": round(avg_api_cov, 4),
        "pass@1": pass_at_k(n_samples, n_pass, 1),
        "pass@4": pass_at_k(n_samples, n_pass, 4),
        "pass@8": pass_at_k(n_samples, n_pass, 8),
        "elapsed": round(elapsed, 1), "samples": results,
    }

def run_profiling(n_per_tier, smoke=False):
    if smoke:
        n_per_tier = 5
        log("SMOKE MODE: 5 tasks/tier")
    if NO_DOCS:
        log("NO_DOCS MODE: API docs NOT included in prompt (harder condition)")
    load_api_docs()
    tasks = load_tasks()
    sampled = sample_by_tier(tasks, n_per_tier)
    log(f"Total: {len(sampled)} tasks x {N_SAMPLES} samples = {len(sampled) * N_SAMPLES} API calls")
    all_results = []
    t_start = time.time()
    for i, task in enumerate(sampled):
        result = evaluate_task(task)
        all_results.append(result)
        log(f"  [{i+1}/{len(sampled)}] {result['task_id']} (L={result['difficulty']} APIs={result['num_apis']}): pass={result['n_pass']}/{N_SAMPLES} p@1={result['pass@1']:.2f} p@8={result['pass@8']:.2f} t={result['elapsed']:.1f}s")
    total_elapsed = time.time() - t_start
    log(f"\nTotal elapsed: {total_elapsed:.1f}s ({total_elapsed/60:.1f}min)")
    tier_stats = {}
    for tier in TIERS:
        tier_results = [r for r in all_results if r["difficulty"] == tier]
        if not tier_results:
            continue
        n_tasks = len(tier_results)
        avg_p1 = sum(r["pass@1"] for r in tier_results) / n_tasks
        avg_p4 = sum(r["pass@4"] for r in tier_results) / n_tasks
        avg_p8 = sum(r["pass@8"] for r in tier_results) / n_tasks
        avg_syntax = sum(r["n_syntax_ok"] for r in tier_results) / (n_tasks * N_SAMPLES)
        avg_api = sum(r["avg_api_coverage"] for r in tier_results) / n_tasks
        p1_values = [r["pass@1"] for r in tier_results]
        p1_var = sum((v - avg_p1) ** 2 for v in p1_values) / n_tasks if n_tasks > 0 else 0
        n_zero = sum(1 for r in tier_results if r["n_pass"] == 0)
        n_full = sum(1 for r in tier_results if r["n_pass"] == N_SAMPLES)
        tier_stats[tier] = {
            "n_tasks": n_tasks, "avg_pass@1": round(avg_p1, 4), "avg_pass@4": round(avg_p4, 4),
            "avg_pass@8": round(avg_p8, 4), "avg_syntax_rate": round(avg_syntax, 4),
            "avg_api_coverage": round(avg_api, 4), "pass@1_std": round(math.sqrt(p1_var), 4),
            "n_zero_pass": n_zero, "n_full_pass": n_full,
            "discriminability": "HIGH" if 0.1 < avg_p1 < 0.9 else ("LOW_CEILING" if avg_p1 >= 0.9 else "LOW_FLOOR"),
        }
    overall = {"total_tasks": len(all_results), "total_api_calls": len(all_results) * N_SAMPLES, "elapsed_sec": round(total_elapsed, 1), "model": SGLANG_MODEL, "temperature": TEMPERATURE, "n_samples": N_SAMPLES, "api_docs": "NO" if NO_DOCS else "YES", "surrogate_warning": "Qwen3.8-27B surrogate NOT transferable to BaiZe"}
    summary = {"overall": overall, "tier_stats": tier_stats, "task_results": all_results}
    log("\n" + "=" * 80)
    log("PASS@8 DIFFICULTY PROFILING SUMMARY")
    log("=" * 80)
    log(f"{'Tier':<6} {'N':>4} {'p@1':>8} {'p@4':>8} {'p@8':>8} {'syntax%':>8} {'api_cov%':>9} {'p@1_std':>8} {'zero':>5} {'full':>5} {'discrim':>12}")
    log("-" * 80)
    for tier in TIERS:
        if tier not in tier_stats:
            continue
        s = tier_stats[tier]
        log(f"{tier:<6} {s['n_tasks']:>4} {s['avg_pass@1']:>8.2f} {s['avg_pass@4']:>8.2f} {s['avg_pass@8']:>8.2f} {s['avg_syntax_rate']*100:>7.1f}% {s['avg_api_coverage']*100:>8.1f}% {s['pass@1_std']:>8.3f} {s['n_zero_pass']:>5} {s['n_full_pass']:>5} {s['discriminability']:>12}")
    log("=" * 80)
    log("\nDISCRIMINABILITY ANALYSIS:")
    tiers_present = [t for t in TIERS if t in tier_stats]
    for i in range(len(tiers_present) - 1):
        t1, t2 = tiers_present[i], tiers_present[i + 1]
        p1_diff = tier_stats[t1]["avg_pass@1"] - tier_stats[t2]["avg_pass@1"]
        direction = "OK" if p1_diff > 0 else "REVERSED"
        log(f"  {t1}->{t2}: delta p@1 = {p1_diff:+.4f} {direction}")
    p1_values = [tier_stats[t]["avg_pass@1"] for t in tiers_present]
    is_monotonic = all(p1_values[i] >= p1_values[i + 1] for i in range(len(p1_values) - 1))
    log(f"\n  Monotonic decrease (L1->L5): {'YES' if is_monotonic else 'NO'}")
    if p1_values:
        spread = max(p1_values) - min(p1_values)
        log(f"  Spread (max-min p@1): {spread:.4f}")
        log(f"  Verdict: {'GOOD separation' if spread > 0.2 else 'POOR separation'}")
    return summary

def generate_html(summary, output_path):
    overall = summary["overall"]
    tier_stats = summary["tier_stats"]
    task_results = summary["task_results"]
    rows = ""
    for tier in TIERS:
        if tier not in tier_stats:
            continue
        s = tier_stats[tier]
        dc = {"HIGH": "#28a745", "LOW_CEILING": "#ffc107", "LOW_FLOOR": "#dc3545"}.get(s["discriminability"], "#6c757d")
        rows += f"<tr><td><b>{tier}</b></td><td>{s['n_tasks']}</td><td>{s['avg_pass@1']:.2%}</td><td>{s['avg_pass@4']:.2%}</td><td>{s['avg_pass@8']:.2%}</td><td>{s['avg_syntax_rate']:.1%}</td><td>{s['avg_api_coverage']:.1%}</td><td>{s['pass@1_std']:.3f}</td><td>{s['n_zero_pass']}</td><td>{s['n_full_pass']}</td><td style='color:{dc}'><b>{s['discriminability']}</b></td></tr>\n"
    tiers_present = [t for t in TIERS if t in tier_stats]
    p1_vals = [tier_stats[t]["avg_pass@1"] for t in tiers_present]
    p8_vals = [tier_stats[t]["avg_pass@8"] for t in tiers_present]
    max_val = max(p1_vals + p8_vals + [0.01])
    bar_chart = ""
    for i, tier in enumerate(tiers_present):
        p1 = p1_vals[i]; p8 = p8_vals[i]
        bar_chart += f"<div style='margin:8px 0'><span style='display:inline-block;width:40px;font-weight:bold'>{tier}</span><span style='display:inline-block;width:60px'>pass@1</span><div style='display:inline-block;background:#007bff;height:16px;width:{p1/max_val*300:.0f}px;border-radius:3px'></div><span style='margin-left:4px'>{p1:.1%}</span></div>\n"
        bar_chart += f"<div style='margin:4px 0'><span style='display:inline-block;width:40px'></span><span style='display:inline-block;width:60px'>pass@8</span><div style='display:inline-block;background:#28a745;height:16px;width:{p8/max_val*300:.0f}px;border-radius:3px'></div><span style='margin-left:4px'>{p8:.1%}</span></div>\n"
    detail_rows = ""
    for tier in tiers_present:
        tier_tasks = sorted([r for r in task_results if r["difficulty"] == tier], key=lambda x: x["pass@1"])
        show = tier_tasks[:2] + tier_tasks[len(tier_tasks)//2:len(tier_tasks)//2+1] + tier_tasks[-2:]
        for r in show:
            detail_rows += f"<tr><td>{r['task_id']}</td><td>{r['difficulty']}</td><td>{r['num_apis']}</td><td>{r['n_pass']}/{r['n_samples']}</td><td>{r['pass@1']:.2f}</td><td>{r['pass@8']:.2f}</td><td>{r['avg_api_coverage']:.1%}</td><td>{r['assertion_template']}</td></tr>\n"
    sep_rows = ""
    p1_values = [tier_stats[t]["avg_pass@1"] for t in tiers_present]
    is_monotonic = all(p1_values[i] >= p1_values[i + 1] for i in range(len(p1_values) - 1))
    spread = max(p1_values) - min(p1_values) if p1_values else 0
    for i in range(len(tiers_present) - 1):
        t1, t2 = tiers_present[i], tiers_present[i + 1]
        p1_diff = tier_stats[t1]["avg_pass@1"] - tier_stats[t2]["avg_pass@1"]
        ok = "YES" if p1_diff > 0 else "REVERSED"
        sep_rows += f"<tr><td>{t1} -> {t2}</td><td>{p1_diff:+.4f}</td><td>{ok}</td></tr>\n"
    html = f"""<!DOCTYPE html><html lang='zh'><head><meta charset='UTF-8'><title>R116 Pass@8</title><style>body{{font-family:system-ui,sans-serif;max-width:1100px;margin:20px auto;padding:0 20px;color:#333}}h1{{color:#1a1a2e;border-bottom:3px solid #007bff;padding-bottom:10px}}h2{{color:#1a1a2e;margin-top:30px;border-left:4px solid #007bff;padding-left:10px}}table{{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px}}th,td{{border:1px solid #ddd;padding:6px 10px;text-align:center}}th{{background:#f8f9fa}}tr:nth-child(even){{background:#f8f9fa}}.warn{{background:#fff3cd;padding:12px 20px;border-radius:8px;margin:10px 0;border-left:4px solid #ffc107}}.info{{background:#d1ecf1;padding:12px 20px;border-radius:8px;margin:10px 0;border-left:4px solid #17a2b8}}</style></head><body><h1>R116: Pass@8 \u96be\u5ea6\u5206\u5c42\u7ecf\u9a8c\u9a8c\u8bc1</h1><p><small>R116 (2026-11-09) | \u96f6 GPU (\u590d\u7528 root SGLang) | \u66ff\u8eab Qwen3.8-27B | R2 \u65b9\u5411</small></p><div class='warn'><b>\u26a0\ufe0f \u66ff\u8eab\u8b66\u544a</b>\uff1a\u7ed3\u679c\u6765\u81ea Qwen3.8-27B\uff0c<b>\u4e0d\u53ef\u8fc1\u79fb\u5230 BaiZe</b>\u3002\u76ee\u7684\u4ec5\u9a8c\u8bc1\u9898\u76ee\u96be\u5ea6\u5206\u5c42\u7684\u5408\u7406\u6027\u3002</div><h2>1. \u5b9e\u9a8c\u8bbe\u8ba1</h2><table><tr><th>\u53c2\u6570</th><th>\u503c</th></tr><tr><td>\u66ff\u8eab\u6a21\u578b</td><td>{overall['model']}</td></tr><tr><td>\u6e29\u5ea6</td><td>{overall['temperature']}</td></tr><tr><td>\u6bcf\u9898\u91c7\u6837</td><td>{overall['n_samples']}</td></tr><tr><td>\u603b\u4efb\u52a1</td><td>{overall['total_tasks']}</td></tr><tr><td>\u603b API \u8c03\u7528</td><td>{overall['total_api_calls']}</td></tr><tr><td>\u8017\u65f6</td><td>{overall['elapsed_sec']}s ({overall['elapsed_sec']/60:.1f}min)</td></tr><tr><td>\u8bc4\u5206</td><td>\u8bed\u6cd5\u6b63\u786e + \u5168\u90e8\u5fc5\u9700 API \u51fa\u73b0 = pass</td></tr></table><h2>2. \u5206\u5c42\u7edf\u8ba1</h2><table><tr><th>\u96be\u5ea6</th><th>\u9898\u6570</th><th>pass@1</th><th>pass@4</th><th>pass@8</th><th>\u8bed\u6cd5\u7387</th><th>API\u8986\u76d6</th><th>p@1\u6807\u51c6\u5dee</th><th>\u96f6\u901a\u8fc7</th><th>\u5168\u901a\u8fc7</th><th>\u533a\u5206\u5ea6</th></tr>{rows}</table><h2>3. pass@1 / pass@8 \u5bf9\u6bd4</h2>{bar_chart}<h2>4. \u5c42\u7ea7\u5206\u79bb\u8d28\u91cf</h2><table><tr><th>\u8dc3\u8fc1</th><th>\u0394 pass@1</th><th>\u65b9\u5411</th></tr>{sep_rows}</table><p><b>\u5355\u8c03\u6027</b>\uff1a{'YES' if is_monotonic else 'NO'}<br><b>\u6781\u5dee</b>\uff1a{spread:.4f} -> {'GOOD (>0.2)' if spread > 0.2 else 'POOR'}</p><h2>5. \u4efb\u52a1\u7ea7\u660e\u7ec6</h2><table><tr><th>Task ID</th><th>\u96be\u5ea6</th><th>API\u6570</th><th>\u901a\u8fc7</th><th>p@1</th><th>p@8</th><th>API\u8986\u76d6</th><th>\u65ad\u8a00</th></tr>{detail_rows}</table><h2>6. R2 \u56de\u7b54</h2><div class='info'><p><b>\u95ee</b>\uff1apass@8 profiling \u8fd8\u662f\u89c4\u5219\u5206\u5c42\uff1f</p><p><b>\u7b54</b>\uff1a\u89c4\u5219\u5206\u5c42\u63d0\u4f9b\u521d\u6b65\u6846\u67b6\uff0cpass@8 profiling \u53ef\u4f5c\u4e3a\u6821\u51c6\u5de5\u5177\u4fee\u6b63\u8fb9\u754c\u3002\u5efa\u8bae\u5bf9\u533a\u5206\u5ea6\u4e0d\u8db3\u7684\u5c42\u7ea7\u8c03\u6574 API \u6570\u91cf\u9608\u503c\u6216\u589e\u52a0 assertion \u590d\u6742\u5ea6\u3002</p></div><h2>7. \u5c40\u9650\u6027</h2><ul><li>\u66ff\u8eab Qwen3.8-27B != MiniCPM5-2B\uff0c\u7edd\u5bf9\u503c\u4e0d\u53ef\u8fc1\u79fb</li><li>\u8bc4\u5206\u57fa\u4e8e API \u8986\u76d6\u7387\u800c\u975e\u6267\u884c\u6b63\u786e\u6027</li><li>\u6bcf\u5c42 30 \u9898\u91c7\u6837\u53ef\u80fd\u4e0d\u4ee3\u8868\u5168\u90e8 3347 \u9898</li></ul><p style='color:#999;font-size:0.8em;margin-top:30px'>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')} | R116 | Qwen3.8-27B via SGLang</p></body></html>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"HTML report: {output_path} ({len(html)} bytes)")

def main():
    parser = argparse.ArgumentParser(description="R116: Pass@8 Difficulty Profiling")
    parser.add_argument("--n", type=int, default=DEFAULT_N_PER_TIER, help="Tasks per tier")
    parser.add_argument("--smoke", action="store_true", help="Smoke test (5 tasks/tier)")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--no-docs", action="store_true", help="Don't include API docs in prompt (harder condition)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    global NO_DOCS
    NO_DOCS = args.no_docs
    summary = run_profiling(args.n, args.smoke)
    suffix = "_nodocs" if NO_DOCS else "_withdocs"
    if args.json:
        json_path = SCRIPT_DIR / f"r116_pass8_profiling{suffix}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        log(f"JSON: {json_path}")
    if args.html:
        html_path = REPORT_DIR / f"report_posttrain_pass8_profiling_r116{suffix}_zh.html"
        generate_html(summary, html_path)
    return summary

if __name__ == "__main__":
    main()
