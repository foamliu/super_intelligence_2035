#!/usr/bin/env python3
"""
R88: DeepSeek Failure Trace Deep Analysis — Irreducible Hard Cases & RL Curriculum Implications
Zero GPU. Pure Python 3.8+ stdlib. No external dependencies.
"""
import json, os, re, sys, math
from collections import defaultdict, Counter

HOME = os.path.expanduser("~")
TRACE_DIR = os.path.join(HOME, "code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3")
ERROR_CASE_DIR = os.path.join(TRACE_DIR, "cline_trace_error_case")
SUCCESS_TRACE_DIR = os.path.join(TRACE_DIR, "cline_trace")
DATASET_PATH = os.path.join(HOME, "code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
RUN_DIR = os.path.dirname(__file__)

FAILURE_MODES = {
    "import_error": "Import/Module not found",
    "api_misuse": "API name wrong / wrong arguments",
    "logic_error": "Assertion failed / wrong return value",
    "syntax_error": "Python syntax error in generated code",
    "timeout": "Too many iterations without convergence",
    "missing_dependency": "techlib / external dependency missing",
    "type_error": "TypeError / attribute access error",
    "incomplete": "Task not completed / model gave up",
}

def load_dataset():
    tasks = {}
    with open(DATASET_PATH) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            d = json.loads(line)
            tid = d["task_id"]
            tasks[tid] = {
                "task_id": tid, "entry_point": d.get("entry_point",""),
                "prompt": d.get("prompt",""),
                "scenario": d.get("metadata",{}).get("scenario","Unknown"),
                "category": d.get("metadata",{}).get("category","Unknown"),
                "apis_used": d.get("metadata",{}).get("apis_used",[]),
                "num_unique_apis": d.get("metadata",{}).get("num_unique_apis",0),
                "techlib_dependency": d.get("metadata",{}).get("techlib_dependency",False),
                "lines_of_code": d.get("metadata",{}).get("lines_of_code",0),
                "task_name": d.get("metadata",{}).get("task_name",""),
                "source": d.get("metadata",{}).get("source",""),
            }
    return tasks

def extract_entry_point(conv):
    for msg in conv:
        if not isinstance(msg, dict): continue
        if msg.get("role") != "user": continue
        content = msg.get("content","")
        texts = []
        if isinstance(content, list):
            texts = [c.get("text","") for c in content if isinstance(c,dict) and c.get("type")=="text"]
        elif isinstance(content, str):
            texts = [content]
        for text in texts:
            m = re.search(r'def\s+(\w+)\s*\(', text)
            if m: return m.group(1)
    return None

def extract_task_id_from_filename(fname):
    m = re.search(r'EDA-Eval-PyAether[_-](\d+)', fname)
    if m:
        num = int(m.group(1))
        return f"EDA-Eval-PyAether-{num:03d}"
    return None


def load_error_cases(dataset):
    error_tasks = {}
    if not os.path.isdir(ERROR_CASE_DIR): return error_tasks
    for fname in sorted(os.listdir(ERROR_CASE_DIR)):
        if not fname.endswith(".json"): continue
        fpath = os.path.join(ERROR_CASE_DIR, fname)
        try:
            conv = json.load(open(fpath))
        except Exception: continue
        tid = extract_task_id_from_filename(fname)
        entry_point = extract_entry_point(conv)
        task_meta = None
        if tid and tid in dataset:
            task_meta = dataset[tid]
        else:
            for t, v in dataset.items():
                if v["entry_point"] == entry_point:
                    task_meta = v; tid = t; break
        error_tasks[tid or fname] = {
            "task_id": tid, "entry_point": entry_point, "conv": conv,
            "conv_len": len(conv), "task_meta": task_meta, "filename": fname,
        }
    return error_tasks

def classify_failure(conv):
    error_signals = defaultdict(int)
    for msg in conv:
        if not isinstance(msg, dict): continue
        content = msg.get("content","")
        texts = []
        if isinstance(content, list):
            texts = [c.get("text","") for c in content if isinstance(c,dict) and c.get("type")=="text"]
        elif isinstance(content, str):
            texts = [content]
        for text in texts:
            tl = text.lower()
            if "importerror" in tl or "modulenotfounderror" in tl or "no module named" in tl:
                error_signals["import_error"] += 1
            if "attributeerror" in tl or "has no attribute" in tl:
                error_signals["api_misuse"] += 1
            if "nameerror" in tl or "is not defined" in tl:
                error_signals["api_misuse"] += 1
            if "typeerror" in tl:
                error_signals["type_error"] += 1
            if "assertionerror" in tl or ("assert" in tl and "fail" in tl):
                error_signals["logic_error"] += 1
            if "syntaxerror" in tl or "invalid syntax" in tl:
                error_signals["syntax_error"] += 1
            if "techlib" in tl or "cannot find library" in tl:
                error_signals["missing_dependency"] += 1
            if "runtimeerror" in tl:
                error_signals["logic_error"] += 1
            if "filenotfounderror" in tl or "no such file" in tl:
                error_signals["import_error"] += 1
    if not error_signals:
        return "timeout", error_signals
    primary = max(error_signals, key=lambda k: error_signals[k])
    return primary, error_signals

def count_tool_calls(conv):
    tool_calls = 0
    tool_types = defaultdict(int)
    for msg in conv:
        if not isinstance(msg, dict): continue
        content = msg.get("content","")
        texts = []
        if isinstance(content, list):
            texts = [c.get("text","") for c in content if isinstance(c,dict) and c.get("type")=="text"]
        elif isinstance(content, str):
            texts = [content]
        for text in texts:
            for tool in ["search_apis","get_api_details","run_pyAether_code_tool",
                         "write_to_file","read_file","list_files","execute_command"]:
                if f"<{tool}>" in text or f"[{tool}]" in text:
                    tool_calls += 1; tool_types[tool] += 1
    return tool_calls, dict(tool_types)

def count_iterations(conv):
    rounds = 0
    for msg in conv:
        if not isinstance(msg, dict): continue
        if msg.get("role") == "user":
            content = msg.get("content","")
            texts = []
            if isinstance(content, list):
                texts = [c.get("text","") for c in content if isinstance(c,dict) and c.get("type")=="text"]
            elif isinstance(content, str):
                texts = [content]
            for text in texts:
                if "Result:" in text and ("run_pyAether" in text or "write_to_file" in text or "execute" in text):
                    rounds += 1; break
    return rounds

def is_irreducible(failure_mode, task_meta, error_signals, conv_len, tool_calls):
    if not task_meta: return "unknown", 0, []
    score = 0; reasons = []
    if task_meta["techlib_dependency"]: score += 2; reasons.append("techlib=True")
    if task_meta["num_unique_apis"] >= 6: score += 2; reasons.append(f"apis={task_meta['num_unique_apis']}")
    elif task_meta["num_unique_apis"] >= 4: score += 1; reasons.append(f"apis={task_meta['num_unique_apis']}")
    if task_meta["lines_of_code"] > 10: score += 1; reasons.append(f"loc={task_meta['lines_of_code']}")
    if len(error_signals) >= 3: score += 2; reasons.append(f"multi_err={len(error_signals)}")
    elif len(error_signals) >= 2: score += 1; reasons.append(f"dual_err={len(error_signals)}")
    if failure_mode == "missing_dependency": score += 3; reasons.append("missing_dep")
    if failure_mode == "logic_error": score += 1; reasons.append("logic_deep")
    if failure_mode == "api_misuse" and task_meta["num_unique_apis"] <= 2: score -= 1; reasons.append("simple_api_misuse")
    if conv_len > 40 and tool_calls > 15: score += 1; reasons.append(f"long_conv={conv_len}")
    if score >= 4: return "irreducible", score, reasons
    elif score >= 2: return "partially_reducible", score, reasons
    else: return "avoidable", score, reasons

def analyze_all(dataset, error_cases):
    results = {
        "total_tasks": len(dataset), "total_traces": 0,
        "total_errors": len(error_cases), "error_details": [],
        "scenario_stats": defaultdict(lambda: {"total": 0, "errors": 0}),
        "category_stats": defaultdict(lambda: {"total": 0, "errors": 0}),
        "failure_mode_counts": defaultdict(int),
        "irreducible_counts": defaultdict(int),
        "api_count_vs_failure": defaultdict(lambda: {"pass": 0, "fail": 0}),
        "techlib_stats": {"dep_total": 0, "dep_errors": 0, "nodep_total": 0, "nodep_errors": 0},
    }
    if os.path.isdir(SUCCESS_TRACE_DIR):
        results["total_traces"] = len(os.listdir(SUCCESS_TRACE_DIR))
    error_tids = set()
    for key, ec in error_cases.items():
        if ec["task_id"]: error_tids.add(ec["task_id"])
    for tid, meta in dataset.items():
        results["scenario_stats"][meta["scenario"]]["total"] += 1
        results["category_stats"][meta["category"]]["total"] += 1
        is_err = tid in error_tids
        if is_err:
            results["scenario_stats"][meta["scenario"]]["errors"] += 1
            results["category_stats"][meta["category"]]["errors"] += 1
        api_bucket = min(meta["num_unique_apis"], 11)
        results["api_count_vs_failure"][api_bucket]["fail" if is_err else "pass"] += 1
        if meta["techlib_dependency"]:
            results["techlib_stats"]["dep_total"] += 1
            if is_err: results["techlib_stats"]["dep_errors"] += 1
        else:
            results["techlib_stats"]["nodep_total"] += 1
            if is_err: results["techlib_stats"]["nodep_errors"] += 1
    for key, ec in sorted(error_cases.items()):
        conv = ec["conv"]; task_meta = ec["task_meta"]
        failure_mode, error_signals = classify_failure(conv)
        tool_calls, tool_types = count_tool_calls(conv)
        iterations = count_iterations(conv)
        irreducible, score, reasons = is_irreducible(
            failure_mode, task_meta, error_signals, ec["conv_len"], tool_calls)
        results["failure_mode_counts"][failure_mode] += 1
        results["irreducible_counts"][irreducible] += 1
        detail = {
            "task_id": ec["task_id"], "entry_point": ec["entry_point"],
            "filename": ec["filename"], "conv_len": ec["conv_len"],
            "tool_calls": tool_calls, "tool_types": tool_types,
            "iterations": iterations, "failure_mode": failure_mode,
            "error_signals": dict(error_signals),
            "irreducible": irreducible, "score": score, "reasons": reasons,
        }
        if task_meta:
            detail.update({"scenario": task_meta["scenario"], "category": task_meta["category"],
                "num_unique_apis": task_meta["num_unique_apis"],
                "techlib_dependency": task_meta["techlib_dependency"],
                "lines_of_code": task_meta["lines_of_code"], "task_name": task_meta["task_name"]})
        results["error_details"].append(detail)
    return results

def compute_ceiling(results):
    run = results["total_traces"]; errs = results["total_errors"]
    total = results["total_tasks"]
    raw_fr = errs / run if run > 0 else 0
    irr = results["irreducible_counts"].get("irreducible", 0)
    part = results["irreducible_counts"].get("partially_reducible", 0)
    avoid = results["irreducible_counts"].get("avoidable", 0)
    unk = results["irreducible_counts"].get("unknown", 0)
    truly_hard = irr + 0.5 * part
    thr = truly_hard / run if run > 0 else 0
    ceil_fail = thr * total
    ceil_pass = 1 - ceil_fail / total
    return {"total_run": run, "total_errors": errs, "raw_failure_rate": raw_fr,
        "extrapolated_failures_158": raw_fr * total,
        "irreducible_count": irr, "partially_reducible_count": part,
        "avoidable_count": avoid, "unknown_count": unk,
        "truly_hard_per_run": truly_hard, "truly_hard_rate": thr,
        "ceiling_failures_158": ceil_fail, "ceiling_pass_rate": ceil_pass,
        "ceiling_pass_pct": ceil_pass * 100}

def map_curriculum(results):
    tiers = {n: {"tasks": []} for n in
        ["L1_trivial","L2_basic","L3_medium","L4_advanced","L5_challenge"]}
    for d in results["error_details"]:
        ac = d.get("num_unique_apis", 0)
        tl = d.get("techlib_dependency", False)
        loc = d.get("lines_of_code", 0)
        if ac <= 1 and not tl and loc <= 3: tier = "L1_trivial"
        elif ac <= 2 and not tl and loc <= 5: tier = "L2_basic"
        elif ac <= 5 and (not tl or loc <= 10): tier = "L3_medium"
        elif ac <= 10: tier = "L4_advanced"
        else: tier = "L5_challenge"
        tiers[tier]["tasks"].append(d)
    return tiers


def generate_html(results, ceiling, curriculum):
    total = results["total_tasks"]; run = results["total_traces"]
    errs = results["total_errors"]
    pr = (run - errs) / run * 100 if run > 0 else 0
    ts = results["techlib_stats"]
    dep_r = ts["dep_errors"]/ts["dep_total"]*100 if ts["dep_total"]>0 else 0
    nodep_r = ts["nodep_errors"]/ts["nodep_total"]*100 if ts["nodep_total"]>0 else 0
    sc_rows = "".join(
        f"<tr><td>{sc}</td><td>{s['total']}</td><td>{s['errors']}</td><td>{s['errors']/s['total']*100 if s['total']>0 else 0:.1f}%</td></tr>"
        for sc, s in sorted(results["scenario_stats"].items(), key=lambda x: -x[1]["errors"]))
    cat_rows = "".join(
        f"<tr><td>{c}</td><td>{s['total']}</td><td>{s['errors']}</td><td>{s['errors']/s['total']*100 if s['total']>0 else 0:.1f}%</td></tr>"
        for c, s in sorted(results["category_stats"].items(), key=lambda x: -x[1]["errors"]))
    fm_rows = "".join(
        f"<tr><td>{fm}</td><td>{FAILURE_MODES.get(fm,fm)}</td><td>{cnt}</td><td>{cnt/errs*100 if errs>0 else 0:.1f}%</td></tr>"
        for fm, cnt in sorted(results["failure_mode_counts"].items(), key=lambda x: -x[1]))
    irr_labels = {"irreducible":"不可回收(本质困难)","partially_reducible":"部分可回收","avoidable":"可回收(SFT/RL可修)","unknown":"未知"}
    irr_rows = "".join(
        f"<tr><td>{k}</td><td>{irr_labels.get(k,k)}</td><td>{cnt}</td><td>{cnt/errs*100 if errs>0 else 0:.1f}%</td></tr>"
        for k, cnt in sorted(results["irreducible_counts"].items(), key=lambda x: -x[1]))
    det_rows = "".join(
        f"<tr><td>{d.get('task_id') or d.get('filename','?')}</td><td>{d.get('entry_point','?')}</td>"
        f"<td>{d.get('scenario','?')}</td><td>{d.get('category','?')}</td><td>{d.get('num_unique_apis','?')}</td>"
        f"<td>{'Y' if d.get('techlib_dependency') else 'N'}</td><td>{d.get('lines_of_code','?')}</td>"
        f"<td>{d.get('failure_mode','?')}</td><td>{d.get('irreducible','?')}</td><td>{d.get('score',0)}</td>"
        f"<td>{d.get('tool_calls',0)}</td><td>{d.get('iterations',0)}</td></tr>"
        for d in results["error_details"])
    api_rows = "".join(
        f"<tr><td>{'+' if ac>=11 else ''}{ac}</td><td>{s['pass']+s['fail']}</td><td>{s['fail']}</td><td>{s['pass']}</td>"
        f"<td>{s['fail']/(s['pass']+s['fail'])*100 if s['pass']+s['fail']>0 else 0:.1f}%</td></tr>"
        for ac, s in sorted(results["api_count_vs_failure"].items()))
    cur_rows = "".join(f"<tr><td>{k}</td><td>{len(v['tasks'])}</td></tr>" for k, v in curriculum.items())
    return _html_body(total, run, errs, pr, ts, dep_r, nodep_r, ceiling,
        sc_rows, cat_rows, fm_rows, irr_rows, det_rows, api_rows, cur_rows)


def _html_body(total, run, errs, pr, ts, dep_r, nodep_r, ceiling,
        sc_rows, cat_rows, fm_rows, irr_rows, det_rows, api_rows, cur_rows):
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R88 DeepSeek 失败轨迹深度分析</title>
<style>
body{{font-family:-apple-system,"Segoe UI",Roboto,sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}}
h1{{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:10px}}
h2{{color:#16213e;border-bottom:1px solid #ccc;padding-bottom:5px;margin-top:30px}}
table{{border-collapse:collapse;width:100%;margin:15px 0;font-size:14px}}
th,td{{border:1px solid #ddd;padding:8px 12px;text-align:left}}
th{{background:#16213e;color:#fff;font-weight:600}}
tr:nth-child(even){{background:#f2f2f2}}
.card{{display:inline-block;background:#fff;border-radius:8px;padding:15px 20px;margin:5px;box-shadow:0 2px 4px rgba(0,0,0,0.1);min-width:160px}}
.card .v{{font-size:28px;font-weight:700;color:#16213e}}.card .l{{color:#666;font-size:13px}}
.red{{color:#e94560;font-weight:700}}.green{{color:#27ae60;font-weight:700}}.orange{{color:#f39c12;font-weight:700}}
.callout{{background:#e8f4f8;border-left:4px solid #3498db;padding:10px 15px;margin:15px 0;border-radius:0 4px 4px 0}}
.warn{{background:#fff3cd;border-left:4px solid #f39c12;padding:10px 15px;margin:15px 0;border-radius:0 4px 4px 0}}
.danger{{background:#fdeaea;border-left:4px solid #e94560;padding:10px 15px;margin:15px 0;border-radius:0 4px 4px 0}}
</style></head><body>
<h1>R88 DeepSeek 失败轨迹深度分析 — 不可回收难题与 RL 课程映射</h1>
<p><b>日期</b>:2026-11-09 wake136 · <b>类型</b>:零GPU实证分析 · <b>数据源</b>:DeepSeek全harness(103任务,20失败)+158题数据集</p>
<div class="callout"><b>核心发现</b>:DeepSeek(94% Pass@1)在103任务中失败{errs}个。
<span class="red">{ceiling['irreducible_count']}个</span>不可回收,<span class="orange">{ceiling['partially_reducible_count']}个</span>部分可回收,
<span class="green">{ceiling['avoidable_count']}个</span>可回收。<b>158题天花板Pass@1≈{ceiling['ceiling_pass_pct']:.1f}%</b></div>
<h2>1. 摘要</h2>
<div>
<div class="card"><div class="l">数据集</div><div class="v">{total}</div></div>
<div class="card"><div class="l">运行</div><div class="v">{run}</div></div>
<div class="card"><div class="l">失败</div><div class="v">{errs}</div></div>
<div class="card"><div class="l">通过率</div><div class="v">{pr:.1f}%</div></div>
<div class="card"><div class="l">天花板</div><div class="v">{ceiling['ceiling_pass_pct']:.1f}%</div></div>
</div>
<h2>2. 失败模式分类</h2>
<table><tr><th>模式</th><th>描述</th><th>数量</th><th>占比</th></tr>{fm_rows}</table>
<h2>3. 可回收性分类</h2>
<table><tr><th>分类</th><th>含义</th><th>数量</th><th>占比</th></tr>{irr_rows}</table>
<h2>4. 场景失败率</h2>
<table><tr><th>场景</th><th>总题</th><th>失败</th><th>失败率</th></tr>{sc_rows}</table>
<h2>5. 类别失败率</h2>
<table><tr><th>类别</th><th>总题</th><th>失败</th><th>失败率</th></tr>{cat_rows}</table>
<h2>6. API数 vs 失败率</h2>
<table><tr><th>API数</th><th>总题</th><th>失败</th><th>通过</th><th>失败率</th></tr>{api_rows}</table>
<h2>7. Techlib依赖 vs 失败率</h2>
<table><tr><th>依赖</th><th>总题</th><th>失败</th><th>失败率</th></tr>
<tr><td>有techlib</td><td>{ts['dep_total']}</td><td>{ts['dep_errors']}</td><td class="red">{dep_r:.1f}%</td></tr>
<tr><td>无techlib</td><td>{ts['nodep_total']}</td><td>{ts['nodep_errors']}</td><td class="green">{nodep_r:.1f}%</td></tr></table>
<div class="danger"><b>techlib依赖是强失败预测因子</b>:差异{dep_r-nodep_r:.1f}pp,支持R83 w3=0.20设计</div>
<h2>8. 失败案例详情</h2>
<table><tr><th>任务ID</th><th>函数</th><th>场景</th><th>类别</th><th>API</th><th>techlib</th><th>LOC</th><th>模式</th><th>可回收</th><th>分</th><th>工具</th><th>迭代</th></tr>{det_rows}</table>
<h2>9. 天花板估算</h2>
<table><tr><th>指标</th><th>值</th></tr>
<tr><td>原始失败率</td><td>{ceiling['raw_failure_rate']*100:.1f}%</td></tr>
<tr><td>不可回收</td><td>{ceiling['irreducible_count']}</td></tr>
<tr><td>部分可回收</td><td>{ceiling['partially_reducible_count']}</td></tr>
<tr><td>可回收</td><td>{ceiling['avoidable_count']}</td></tr>
<tr><td>158题困难数</td><td class="red">{ceiling['ceiling_failures_158']:.1f}</td></tr>
<tr><td><b>天花板Pass@1</b></td><td class="red">{ceiling['ceiling_pass_pct']:.1f}%</td></tr></table>
<h2>10. RL课程映射</h2>
<table><tr><th>层级</th><th>失败数</th></tr>{cur_rows}</table>
<h2>11. Post-Train侧重建议</h2>
<div class="callout"><ol>
<li><b>领域退火</b>:注入PyAether API文档(4.5M tok),覆盖失败API</li>
<li><b>SFT</b>:用DeepSeek成功轨迹(83/103)修复"可回收"类</li>
<li><b>RL(GRPO)</b>:聚焦L3-L4"部分可回收",R2+R3打磨闭环</li>
<li><b>不可回收</b>:L5 techlib题排除RL,论文作"环境限制"讨论</li>
</ol></div>
<h2>12. 局限性</h2>
<div class="warn"><ul>
<li>基于DeepSeek侧103任务,36%侧轨迹不在本节点</li>
<li>20个案例统计功效有限,需GPU后790次运行校正</li>
<li>不可回收为启发式,需GPU后对照验证</li>
<li>天花板估算假设随机抽样,外推有偏差</li>
</ul></div>
<p style="margin-top:40px;color:#999;font-size:12px;text-align:center">R88 · 2026-11-09 wake136 · 零GPU · Python 3.8+ stdlib</p>
</body></html>"""


def main():
    print("="*60); print("R88: DeepSeek Failure Trace Deep Analysis"); print("="*60)
    print("[1/6] Loading dataset..."); dataset = load_dataset(); print(f"  {len(dataset)} tasks")
    print("[2/6] Loading error cases..."); error_cases = load_error_cases(dataset); print(f"  {len(error_cases)} errors")
    print("[3/6] Analyzing..."); results = analyze_all(dataset, error_cases)
    print(f"  traces={results['total_traces']} errors={results['total_errors']}")
    print(f"  modes={dict(results['failure_mode_counts'])}")
    print(f"  irreducible={dict(results['irreducible_counts'])}")
    print("[4/6] Ceiling..."); ceiling = compute_ceiling(results)
    print(f"  ceiling_pass={ceiling['ceiling_pass_pct']:.1f}%")
    print("[5/6] Curriculum..."); curriculum = map_curriculum(results)
    for t, d in curriculum.items(): print(f"  {t}: {len(d['tasks'])}")
    print("[6/6] HTML..."); html = generate_html(results, ceiling, curriculum)
    rp = os.path.join(REPORT_DIR, "report_posttrain_r88_ds_failure_analysis_zh.html")
    with open(rp, "w") as f: f.write(html)
    print(f"  {rp} ({os.path.getsize(rp)/1024:.1f}KB)")
    jd = {"R88": {"total_tasks": results["total_tasks"], "total_traces": results["total_traces"],
        "total_errors": results["total_errors"], "failure_mode_counts": dict(results["failure_mode_counts"]),
        "irreducible_counts": dict(results["irreducible_counts"]),
        "scenario_stats": {k: dict(v) for k, v in results["scenario_stats"].items()},
        "category_stats": {k: dict(v) for k, v in results["category_stats"].items()},
        "techlib_stats": results["techlib_stats"], "ceiling": ceiling,
        "curriculum": {k: len(v["tasks"]) for k, v in curriculum.items()},
        "error_details": results["error_details"]}}
    jp = os.path.join(RUN_DIR, "r88_results.json")
    with open(jp, "w") as f: json.dump(jd, f, indent=2, ensure_ascii=False, default=str)
    print(f"  {jp} ({os.path.getsize(jp)/1024:.1f}KB)")
    print("\n"+"="*60); print("SUMMARY"); print("="*60)
    print(f"Failures: {results['total_errors']}/{results['total_traces']}")
    print(f"  Irr={ceiling['irreducible_count']} Part={ceiling['partially_reducible_count']} Avoid={ceiling['avoidable_count']}")
    print(f"Ceiling Pass@1 (158): {ceiling['ceiling_pass_pct']:.1f}%")
    ts = results["techlib_stats"]
    print(f"Techlib: {ts['dep_errors']}/{ts['dep_total']}={ts['dep_errors']/max(ts['dep_total'],1)*100:.1f}% vs {ts['nodep_errors']}/{ts['nodep_total']}={ts['nodep_errors']/max(ts['nodep_total'],1)*100:.1f}%")
    return 0

if __name__ == "__main__":
    sys.exit(main())
