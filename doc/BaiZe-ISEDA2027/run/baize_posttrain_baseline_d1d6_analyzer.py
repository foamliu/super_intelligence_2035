#!/usr/bin/env python3
"""
baize_posttrain_baseline_d1d6_analyzer.py — R55: Automated Post-Baseline D1-D6 Analysis Pipeline

Purpose:
  After the 11/9 MiniCPM5-2B baseline run on EDA-Eval-PyAether (158 tasks),
  this script automatically extracts the D1-D6 diagnostic metrics from the
  fresh traces and final_report.json — filling the long-standing gap where
  MiniCPM5-2B side data was "not on this node".

  It also compares with DeepSeek side data (if available) to quantify how
  much of the 58 pp gap is "protocol-recoverable" vs "real capability gap".

Inputs:
  --report-json  : final_report.json from the baseline run (required)
  --trace-dir    : cline_cli_trace/<version>/cline_trace/ directory (optional)
  --dataset-jsonl: EDA-Eval-PyAether-v20260311.jsonl for scenario metadata
  --deepseek-report-json : DeepSeek side final_report.json for comparison
  --deepseek-trace-dir  : DeepSeek side trace directory for comparison
  --html         : path to output HTML report
  --json-out     : path to output JSON summary (default: stdout)

D1-D6 definitions (from README.md 7.0):
  D1: Tool call legality rate (format-valid tool_call / total)
  D2: Tool call frequency (avg calls per task)
  D3: Timeout/truncation ratio
  D4: Failure type decomposition (execution errors vs assertion failures)
  D5: Per-scenario pass rate (Layout 64 / Schematic 47 / Design Mgmt 24 / Others 23)
  D6: Average iteration rounds (Phi) distribution

Author: posttrain agent (R55, wake103, 2026-11-08)
"""

import argparse
import json
import os
import sys
import statistics
from collections import Counter, defaultdict
from pathlib import Path

DEFAULT_DATASET = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/"
    "EDA-Eval-PyAether-v20260311.jsonl"
)
DEFAULT_DEEPSEEK_TRACE = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/cline_cli_trace/"
    "cline_trace_v1_3/cline_trace"
)

_TP_AVAILABLE = False
try:
    import importlib.util
    _TP_PATH = os.path.expanduser("~/code/eda_fastmcp/memory_bank/trace_parser.py")
    if os.path.exists(_TP_PATH):
        _spec = importlib.util.spec_from_file_location("trace_parser", _TP_PATH)
        tp = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(tp)
        _TP_AVAILABLE = True
except Exception:
    pass

# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def load_report(report_path):
    if not report_path or not os.path.exists(report_path):
        return None
    with open(report_path) as f:
        return json.load(f)

def load_dataset(dataset_path):
    path = dataset_path or DEFAULT_DATASET
    if not os.path.exists(path):
        return {}
    result = {}
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            tid = d.get("task_id", "")
            result[tid] = d.get("metadata", {})
    return result

def find_trace_dirs(trace_dir):
    if not trace_dir or not os.path.isdir(trace_dir):
        return []
    entries = sorted(os.listdir(trace_dir))
    dirs = []
    for e in entries:
        full = os.path.join(trace_dir, e)
        if os.path.isdir(full) and os.path.exists(os.path.join(full, "api_conversation_history.json")):
            dirs.append(full)
    return dirs

def load_trace(trace_path):
    p = os.path.join(trace_path, "api_conversation_history.json")
    if not os.path.exists(p):
        return []
    with open(p) as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "messages" in data:
        return data["messages"]
    return []

def load_task_metadata(trace_path):
    p = os.path.join(trace_path, "task_metadata.json")
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return json.load(f)

# ---------------------------------------------------------------------------
# D1-D6 extraction from final_report.json (no traces needed)
# ---------------------------------------------------------------------------

def extract_from_report(report, dataset_meta):
    details = report.get("details_per_task", {})
    summary = report.get("summary", {})
    metrics = report.get("metrics", {})
    total_tasks = len(details)
    total_pass = 0

    gen_stats = summary.get("generation_statistics", {})
    gen_timeout = gen_stats.get("timeout", 0)
    gen_failure = gen_stats.get("failure", 0)
    gen_success = gen_stats.get("success", 0)
    total_gen = gen_timeout + gen_failure + gen_success
    timeout_ratio = gen_timeout / total_gen if total_gen > 0 else 0.0

    error_type_counter = Counter()
    exec_error_count = 0
    assertion_fail_count = 0
    for tid, info in details.items():
        pass_rate = info.get("pass_rate", 0)
        if pass_rate >= 1.0:
            total_pass += 1
        error_types = info.get("error_types", [])
        for et in error_types:
            if isinstance(et, str):
                error_type_counter[et] += 1
                et_lower = et.lower()
                if "assert" in et_lower:
                    assertion_fail_count += 1
                else:
                    exec_error_count += 1
            elif isinstance(et, dict):
                et_name = et.get("type", et.get("error", "unknown"))
                error_type_counter[et_name] += 1
                et_lower = str(et_name).lower()
                if "assert" in et_lower:
                    assertion_fail_count += 1
                else:
                    exec_error_count += 1

    scenario_stats = defaultdict(lambda: {"total": 0, "pass": 0})
    for tid, info in details.items():
        meta = dataset_meta.get(tid, {})
        scenario = meta.get("scenario", "Unknown")
        scenario_stats[scenario]["total"] += 1
        if info.get("pass_rate", 0) >= 1.0:
            scenario_stats[scenario]["pass"] += 1

    scenario_pass_rates = {}
    for sc, stats in sorted(scenario_stats.items()):
        rate = stats["pass"] / stats["total"] if stats["total"] > 0 else 0
        scenario_pass_rates[sc] = {"total": stats["total"], "pass": stats["pass"], "pass_rate": round(rate, 4)}

    overall_pass = metrics.get("pass_rate", 0)
    if not overall_pass and total_tasks > 0:
        overall_pass = total_pass / total_tasks

    return {
        "model_name": report.get("model_name", "unknown"),
        "evaluation_mode": report.get("evaluation_mode", "unknown"),
        "total_tasks": total_tasks,
        "overall_pass_rate": round(overall_pass, 4),
        "D3_timeout_ratio": round(timeout_ratio, 4),
        "D3_timeout_count": gen_timeout,
        "D3_gen_failure_count": gen_failure,
        "D3_gen_success_count": gen_success,
        "D4_error_types": dict(error_type_counter.most_common(20)),
        "D4_exec_error_count": exec_error_count,
        "D4_assertion_fail_count": assertion_fail_count,
        "D4_exec_vs_assert_ratio": {
            "exec_pct": round(exec_error_count / (exec_error_count + assertion_fail_count) * 100, 1) if (exec_error_count + assertion_fail_count) > 0 else 0,
            "assert_pct": round(assertion_fail_count / (exec_error_count + assertion_fail_count) * 100, 1) if (exec_error_count + assertion_fail_count) > 0 else 0,
        },
        "D5_per_scenario": scenario_pass_rates,
    }

# ---------------------------------------------------------------------------
# D1, D2, D6 extraction from traces (requires trace_dir)
# ---------------------------------------------------------------------------

def extract_from_traces(trace_dirs):
    total_tool_calls = 0
    total_valid_tool_calls = 0
    calls_per_task = []
    iterations_per_task = []
    error_classifications = Counter()
    tasks_with_traces = 0
    tasks_without_traces = 0

    for tdir in trace_dirs:
        trace = load_trace(tdir)
        if not trace:
            tasks_without_traces += 1
            continue
        tasks_with_traces += 1

        if _TP_AVAILABLE:
            try:
                tool_calls = tp.extract_tool_calls_from_trace(trace)
                tool_results = tp.extract_tool_results_from_trace(trace)
                num_calls = len(tool_calls)
                total_tool_calls += num_calls
                valid = sum(1 for tc in tool_calls if tc.get("name") and tc.get("name") != "unknown")
                total_valid_tool_calls += valid
                calls_per_task.append(num_calls)
                code_execs = [tc for tc in tool_calls if tc.get("name", "").lower() in ("execute_code", "run_code", "write_to_file", "replace_in_file")]
                iterations = max(1, len(code_execs))
                iterations_per_task.append(iterations)
                for tr in tool_results:
                    err = tr.get("error", "")
                    if err:
                        classified = tp.classify_error(err)
                        error_classifications[classified] += 1
            except Exception:
                calls_per_task.append(len(trace))
                iterations_per_task.append(1)
        else:
            assistant_msgs = [m for m in trace if m.get("role") == "assistant"]
            calls_per_task.append(len(assistant_msgs))
            iterations_per_task.append(max(1, len(assistant_msgs) // 2))

    d1_legality = total_valid_tool_calls / total_tool_calls if total_tool_calls > 0 else 0
    d2_avg_calls = statistics.mean(calls_per_task) if calls_per_task else 0
    d2_median_calls = statistics.median(calls_per_task) if calls_per_task else 0
    d6_avg_iter = statistics.mean(iterations_per_task) if iterations_per_task else 0
    d6_median_iter = statistics.median(iterations_per_task) if iterations_per_task else 0

    iter_dist = Counter()
    for it in iterations_per_task:
        if it <= 2: iter_dist["1-2"] += 1
        elif it <= 4: iter_dist["3-4"] += 1
        elif it <= 6: iter_dist["5-6"] += 1
        elif it <= 10: iter_dist["7-10"] += 1
        else: iter_dist["10+"] += 1

    return {
        "tasks_with_traces": tasks_with_traces,
        "tasks_without_traces": tasks_without_traces,
        "D1_tool_call_legality": round(d1_legality, 4),
        "D1_total_tool_calls": total_tool_calls,
        "D1_valid_tool_calls": total_valid_tool_calls,
        "D2_avg_calls_per_task": round(d2_avg_calls, 2),
        "D2_median_calls_per_task": d2_median_calls,
        "D2_calls_distribution": dict(Counter(calls_per_task).most_common(10)),
        "D6_avg_iterations": round(d6_avg_iter, 2),
        "D6_median_iterations": d6_median_iter,
        "D6_iteration_distribution": dict(iter_dist),
        "D4_trace_error_classifications": dict(error_classifications.most_common(15)),
        "trace_parser_available": _TP_AVAILABLE,
    }

# ---------------------------------------------------------------------------
# Comparison and gap analysis
# ---------------------------------------------------------------------------

def compare_sides(minicpm5, deepseek):
    comparison = {
        "minicpm5_pass_rate": minicpm5.get("overall_pass_rate", 0),
        "deepseek_pass_rate": deepseek.get("overall_pass_rate", 0) if deepseek else None,
        "gap_pp": None,
        "D3_comparison": None,
        "D4_comparison": None,
        "D5_comparison": None,
    }

    if deepseek:
        m_pass = minicpm5.get("overall_pass_rate", 0)
        d_pass = deepseek.get("overall_pass_rate", 0)
        comparison["gap_pp"] = round((d_pass - m_pass) * 100, 1)
        comparison["D3_comparison"] = {
            "minicpm5_timeout_ratio": minicpm5.get("D3_timeout_ratio", 0),
            "deepseek_timeout_ratio": deepseek.get("D3_timeout_ratio", 0),
        }
        m_d4 = minicpm5.get("D4_exec_vs_assert_ratio", {})
        d_d4 = deepseek.get("D4_exec_vs_assert_ratio", {})
        comparison["D4_comparison"] = {"minicpm5": m_d4, "deepseek": d_d4}
        m_d5 = minicpm5.get("D5_per_scenario", {})
        d_d5 = deepseek.get("D5_per_scenario", {})
        comparison["D5_comparison"] = {}
        for sc in sorted(set(list(m_d5.keys()) + list(d_d5.keys()))):
            comparison["D5_comparison"][sc] = {"minicpm5": m_d5.get(sc, {}), "deepseek": d_d5.get(sc, {})}

    if deepseek and comparison["gap_pp"]:
        gap = comparison["gap_pp"]
        m_traces = minicpm5.get("trace_analysis", {})
        d_traces = deepseek.get("trace_analysis", {})
        m_d1 = m_traces.get("D1_tool_call_legality", 0)
        d_d1 = d_traces.get("D1_tool_call_legality", 0)
        m_d2 = m_traces.get("D2_avg_calls_per_task", 0)
        d_d2 = d_traces.get("D2_avg_calls_per_task", 0)
        m_d6 = m_traces.get("D6_avg_iterations", 0)
        d_d6 = d_traces.get("D6_avg_iterations", 0)
        protocol_gap_estimate = 0
        if d_d1 > 0 and m_d1 < d_d1:
            protocol_gap_estimate += (d_d1 - m_d1) * 20
        if d_d2 > 0 and m_d2 < d_d2:
            protocol_gap_estimate += min(15, (d_d2 - m_d2) * 2)
        if d_d6 > 0 and m_d6 < d_d6:
            protocol_gap_estimate += min(15, (d_d6 - m_d6) * 3)
        protocol_gap_estimate = min(protocol_gap_estimate, gap * 0.8)
        real_capability_gap = gap - protocol_gap_estimate
        comparison["gap_analysis"] = {
            "total_gap_pp": gap,
            "protocol_recoverable_estimate_pp": round(protocol_gap_estimate, 1),
            "real_capability_gap_estimate_pp": round(real_capability_gap, 1),
            "protocol_recoverable_pct": round(protocol_gap_estimate / gap * 100, 1) if gap > 0 else 0,
            "method": "heuristic: D1 diff*20 + D2 diff*2(cap15) + D6 diff*3(cap15), capped 80%",
            "d1_diff": round(d_d1 - m_d1, 4) if d_d1 and m_d1 else None,
            "d2_diff": round(d_d2 - m_d2, 2) if d_d2 and m_d2 else None,
            "d6_diff": round(d_d6 - m_d6, 2) if d_d6 and m_d6 else None,
        }
    return comparison

# ---------------------------------------------------------------------------
# HTML report generation
# ---------------------------------------------------------------------------

def generate_html(result, output_path):
    m = result.get("minicpm5", {})
    d = result.get("deepseek")
    comp = result.get("comparison", {})
    mt = m.get("trace_analysis", {})
    dt = d.get("trace_analysis", {}) if d else {}
    gap = comp.get("gap_pp", "\u2014")
    gap_analysis = comp.get("gap_analysis", {})

    d5_rows = ""
    d5_comp = comp.get("D5_comparison", {})
    if d5_comp:
        for sc, vals in d5_comp.items():
            m5 = vals.get("minicpm5", {})
            d5v = vals.get("deepseek", {})
            m_rate = f"{m5.get('pass_rate', 0)*100:.1f}%" if m5 else "\u2014"
            d_rate = f"{d5v.get('pass_rate', 0)*100:.1f}%" if d5v else "\u2014"
            m_cnt = f"{m5.get('pass',0)}/{m5.get('total',0)}" if m5 else "\u2014"
            d_cnt = f"{d5v.get('pass',0)}/{d5v.get('total',0)}" if d5v else "\u2014"
            d5_rows += f"<tr><td>{sc}</td><td>{m_cnt}</td><td>{m_rate}</td><td>{d_cnt}</td><td>{d_rate}</td></tr>"
    else:
        for sc, vals in m.get("D5_per_scenario", {}).items():
            d5_rows += f"<tr><td>{sc}</td><td>{vals.get('pass',0)}/{vals.get('total',0)}</td><td>{vals.get('pass_rate',0)*100:.1f}%</td><td>\u2014</td><td>\u2014</td></tr>"

    m_d4 = m.get("D4_error_types", {})
    d4_rows = ""
    all_errs = set(list(m_d4.keys()) + (list(d.get("D4_error_types", {}).keys()) if d else []))
    for et in sorted(all_errs):
        m_cnt = m_d4.get(et, 0)
        d_cnt = d.get("D4_error_types", {}).get(et, 0) if d else 0
        d4_rows += f"<tr><td>{et}</td><td>{m_cnt}</td><td>{d_cnt}</td></tr>"

    m_d6 = mt.get("D6_iteration_distribution", {})
    d6_rows = ""
    all_buckets = sorted(set(list(m_d6.keys()) + (list(dt.get("D6_iteration_distribution", {}).keys()) if dt else [])))
    for bucket in all_buckets:
        m_cnt = m_d6.get(bucket, 0)
        d_cnt = dt.get("D6_iteration_distribution", {}).get(bucket, 0) if dt else 0
        d6_rows += f"<tr><td>{bucket}</td><td>{m_cnt}</td><td>{d_cnt}</td></tr>"

    gap_section = ""
    if gap_analysis:
        gap_section = f"""
        <section>
            <h2>Gap \u5206\u6790\uff1a58 pp \u5dee\u8ddd\u5206\u89e3</h2>
            <table class="data">
                <tr><th>\u6307\u6807</th><th>\u503c</th></tr>
                <tr><td>\u603b\u5dee\u8ddd</td><td>{gap_analysis.get('total_gap_pp','\u2014')} pp</td></tr>
                <tr><td>\u534f\u8bae\u53ef\u56de\u6536\uff08\u4f30\u8ba1\uff09</td><td>{gap_analysis.get('protocol_recoverable_estimate_pp','\u2014')} pp ({gap_analysis.get('protocol_recoverable_pct','\u2014')}%)</td></tr>
                <tr><td>\u771f\u5b9e\u80fd\u529b\u5dee\u8ddd\uff08\u4f30\u8ba1\uff09</td><td>{gap_analysis.get('real_capability_gap_estimate_pp','\u2014')} pp</td></tr>
                <tr><td>D1 \u5408\u6cd5\u7387\u5dee\u5f02</td><td>{gap_analysis.get('d1_diff','\u2014')}</td></tr>
                <tr><td>D2 \u8c03\u7528\u9891\u6b21\u5dee\u5f02</td><td>{gap_analysis.get('d2_diff','\u2014')}</td></tr>
                <tr><td>D6 \u8fed\u4ee3\u8f6e\u6570\u5dee\u5f02</td><td>{gap_analysis.get('d6_diff','\u2014')}</td></tr>
            </table>
            <p><strong>\u5bf9 post-train \u4e09\u6b65\u7684\u4fa7\u91cd\u5efa\u8bae</strong>\uff1a</p>
            <ul>
                <li>\u534f\u8bae\u53ef\u56de\u6536\u5360\u6bd4\u9ad8 \u2192 SFT \u6ce8\u5165\u5de5\u5177\u8f68\u8ff9+API \u8bed\u6599\u4f18\u5148</li>
                <li>\u771f\u5b9e\u80fd\u529b\u5dee\u8ddd\u5360\u6bd4\u9ad8 \u2192 RL(GRPO) \u6253\u78e8\u95ed\u73af\u63a8\u7406\u662f\u4e3b\u6218\u573a</li>
                <li>D4 \u6267\u884c\u62a5\u9519\u591a \u2192 \u9886\u57df\u9000\u706b\u8865 API \u77e5\u8bc6</li>
                <li>D4 \u65ad\u8a00\u5931\u8d25\u591a \u2192 \u8bed\u4e49\u63a8\u7406\u95ee\u9898\uff0cRL \u4ef7\u503c\u66f4\u5927</li>
            </ul>
        </section>"""

    deepseek_section = ""
    if d:
        deepseek_section = f"""
        <section>
            <h2>DeepSeek \u5bf9\u7167\u4fa7 (94%)</h2>
            <table class="data">
                <tr><th>\u6307\u6807</th><th>\u503c</th></tr>
                <tr><td>\u6a21\u578b</td><td>{d.get('model_name','\u2014')}</td></tr>
                <tr><td>\u603b\u901a\u8fc7\u7387</td><td>{d.get('overall_pass_rate',0)*100:.1f}%</td></tr>
                <tr><td>D1 \u5de5\u5177\u8c03\u7528\u5408\u6cd5\u7387</td><td>{dt.get('D1_tool_call_legality','\u2014')}</td></tr>
                <tr><td>D2 \u5e73\u5747\u8c03\u7528\u9891\u6b21</td><td>{dt.get('D2_avg_calls_per_task','\u2014')}</td></tr>
                <tr><td>D3 \u8d85\u65f6\u6bd4\u4f8b</td><td>{f'{(d or {}).get("D3_timeout_ratio",0)*100:.1f}%' if d else '\u2014'}</td></tr>
                <tr><td>D6 \u5e73\u5747\u8fed\u4ee3\u8f6e\u6570</td><td>{dt.get('D6_avg_iterations','\u2014')}</td></tr>
            </table>
        </section>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R55: Post-Baseline D1-D6 \u81ea\u52a8\u5206\u6790\u62a5\u544a</title>
<style>
body {{ font-family: -apple-system, "Noto Sans SC", sans-serif; max-width: 960px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }}
h1 {{ color: #1a5276; border-bottom: 3px solid #2980b9; padding-bottom: 10px; }}
h2 {{ color: #2874a6; margin-top: 30px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #f2f6fa; font-weight: 600; }}
tr:nth-child(even) {{ background: #fafafa; }}
.summary-box {{ background: #eaf2f8; border-left: 4px solid #2980b9; padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0; }}
.metric {{ display: inline-block; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 6px 14px; margin: 4px; font-size: 0.9em; }}
.metric strong {{ color: #2980b9; }}
code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
section {{ margin-bottom: 30px; }}
</style>
</head>
<body>
<h1>R55: Post-Baseline D1-D6 \u81ea\u52a8\u5206\u6790\u62a5\u544a</h1>
<p><small>\u751f\u6210\u65f6\u95f4\uff1a{result.get('generated_at','\u2014')} | \u811a\u672c\uff1abaize_posttrain_baseline_d1d6_analyzer.py | R55 / wake103</small></p>
<div class="summary-box">
<p><strong>\u76ee\u7684</strong>\uff1a\u4ece 11/9 MiniCPM5-2B \u57fa\u7ebf\u8fd0\u884c\u7684 fresh traces + final_report.json \u81ea\u52a8\u63d0\u53d6 D1-D6\uff0c\u586b\u8865\u6b64\u524d MiniCPM5-2B \u4fa7\u6570\u636e \"not on this node\" \u7684\u7a7a\u767d\u3002\u5e76\u4e0e DeepSeek 94% \u4fa7\u5bf9\u7167\uff0c\u91cf\u5316 58 pp \u5dee\u8ddd\u4e2d\u300c\u534f\u8bae\u53ef\u56de\u6536\u300dvs\u300c\u771f\u5b9e\u80fd\u529b\u5dee\u8ddd\u300d\u7684\u5360\u6bd4\u3002</p>
</div>
<section>
    <h2>MiniCPM5-2B \u57fa\u7ebf\u4fa7 (36%)</h2>
    <table class="data">
        <tr><th>\u6307\u6807</th><th>\u503c</th></tr>
        <tr><td>\u6a21\u578b</td><td>{m.get('model_name','\u2014')}</td></tr>
        <tr><td>\u8bc4\u6d4b\u6a21\u5f0f</td><td>{m.get('evaluation_mode','\u2014')}</td></tr>
        <tr><td>\u603b\u4efb\u52a1\u6570</td><td>{m.get('total_tasks','\u2014')}</td></tr>
        <tr><td>\u603b\u901a\u8fc7\u7387</td><td>{m.get('overall_pass_rate',0)*100:.1f}%</td></tr>
    </table>
    <p>
        <span class="metric">D1 \u5408\u6cd5\u7387: <strong>{mt.get('D1_tool_call_legality','\u2014')}</strong></span>
        <span class="metric">D2 \u8c03\u7528/\u4efb\u52a1: <strong>{mt.get('D2_avg_calls_per_task','\u2014')}</strong></span>
        <span class="metric">D3 \u8d85\u65f6: <strong>{m.get('D3_timeout_ratio',0)*100:.1f}%</strong></span>
        <span class="metric">D6 \u8fed\u4ee3: <strong>{mt.get('D6_avg_iterations','\u2014')}</strong></span>
    </p>
</section>
<section>
    <h2>D1: \u5de5\u5177\u8c03\u7528\u5408\u6cd5\u7387</h2>
    <table class="data">
        <tr><th>\u6307\u6807</th><th>MiniCPM5-2B</th><th>DeepSeek</th></tr>
        <tr><td>\u5408\u6cd5\u7387</td><td>{mt.get('D1_tool_call_legality','\u2014')}</td><td>{dt.get('D1_tool_call_legality','\u2014') if dt else '\u2014'}</td></tr>
        <tr><td>\u603b\u8c03\u7528\u6570</td><td>{mt.get('D1_total_tool_calls','\u2014')}</td><td>{dt.get('D1_total_tool_calls','\u2014') if dt else '\u2014'}</td></tr>
        <tr><td>\u6709\u8f68\u8ff9\u4efb\u52a1\u6570</td><td>{mt.get('tasks_with_traces','\u2014')}</td><td>{dt.get('tasks_with_traces','\u2014') if dt else '\u2014'}</td></tr>
    </table>
    <p><small>\u5224\u8bfb\uff1a&lt;90% \u2192 \u534f\u8bae\u95ee\u9898\uff0cSFT \u53ef\u5927\u5e45\u56de\u6536</small></p>
</section>
<section>
    <h2>D2: \u5de5\u5177\u8c03\u7528\u9891\u6b21</h2>
    <table class="data">
        <tr><th>\u6307\u6807</th><th>MiniCPM5-2B</th><th>DeepSeek</th></tr>
        <tr><td>\u5e73\u5747\u8c03\u7528/\u4efb\u52a1</td><td>{mt.get('D2_avg_calls_per_task','\u2014')}</td><td>{dt.get('D2_avg_calls_per_task','\u2014') if dt else '\u2014'}</td></tr>
        <tr><td>\u4e2d\u4f4d\u8c03\u7528/\u4efb\u52a1</td><td>{mt.get('D2_median_calls_per_task','\u2014')}</td><td>{dt.get('D2_median_calls_per_task','\u2014') if dt else '\u2014'}</td></tr>
    </table>
</section>
<section>
    <h2>D3: \u8d85\u65f6/\u622a\u65ad\u6bd4\u4f8b</h2>
    <table class="data">
        <tr><th>\u6307\u6807</th><th>MiniCPM5-2B</th><th>DeepSeek</th></tr>
        <tr><td>\u8d85\u65f6\u6bd4\u4f8b</td><td>{m.get('D3_timeout_ratio',0)*100:.1f}%</td><td>{f'{(d or {}).get("D3_timeout_ratio",0)*100:.1f}%' if d else '\u2014'}</td></tr>
        <tr><td>\u8d85\u65f6\u6570</td><td>{m.get('D3_timeout_count','\u2014')}</td><td>{d.get('D3_timeout_count','\u2014') if d else '\u2014'}</td></tr>
    </table>
</section>
<section>
    <h2>D4: \u5931\u8d25\u7c7b\u578b\u5206\u89e3</h2>
    <table class="data">
        <tr><th>\u6307\u6807</th><th>MiniCPM5-2B</th><th>DeepSeek</th></tr>
        <tr><td>\u6267\u884c\u62a5\u9519\u6570</td><td>{m.get('D4_exec_error_count','\u2014')}</td><td>{(d or {}).get('D4_exec_error_count','\u2014') if d else '\u2014'}</td></tr>
        <tr><td>\u65ad\u8a00\u5931\u8d25\u6570</td><td>{m.get('D4_assertion_fail_count','\u2014')}</td><td>{(d or {}).get('D4_assertion_fail_count','\u2014') if d else '\u2014'}</td></tr>
        <tr><td>\u6267\u884c\u62a5\u9519\u5360\u6bd4</td><td>{m.get('D4_exec_vs_assert_ratio',{}).get('exec_pct','\u2014')}%</td><td>{(d or {}).get('D4_exec_vs_assert_ratio',{}).get('exec_pct','\u2014') if d else '\u2014'}%</td></tr>
    </table>
    {f"<table class='data'><tr><th>\u9519\u8bef\u7c7b\u578b</th><th>MiniCPM5-2B</th><th>DeepSeek</th></tr>{d4_rows}</table>" if d4_rows else ""}
</section>
<section>
    <h2>D5: Per-Scenario \u901a\u8fc7\u7387</h2>
    <table class="data">
        <tr><th>Scenario</th><th>MiniCPM5 \u901a\u8fc7</th><th>MiniCPM5 \u7387</th><th>DeepSeek \u901a\u8fc7</th><th>DeepSeek \u7387</th></tr>
        {d5_rows}
    </table>
</section>
<section>
    <h2>D6: \u5e73\u5747\u8fed\u4ee3\u8f6e\u6570 (\u03a6) \u5206\u5e03</h2>
    <table class="data">
        <tr><th>\u6307\u6807</th><th>MiniCPM5-2B</th><th>DeepSeek</th></tr>
        <tr><td>\u5e73\u5747\u8fed\u4ee3</td><td>{mt.get('D6_avg_iterations','\u2014')}</td><td>{dt.get('D6_avg_iterations','\u2014') if dt else '\u2014'}</td></tr>
        <tr><td>\u4e2d\u4f4d\u8fed\u4ee3</td><td>{mt.get('D6_median_iterations','\u2014')}</td><td>{dt.get('D6_median_iterations','\u2014') if dt else '\u2014'}</td></tr>
    </table>
    {f"<table class='data'><tr><th>\u8f6e\u6570\u533a\u95f4</th><th>MiniCPM5-2B</th><th>DeepSeek</th></tr>{d6_rows}</table>" if d6_rows else ""}
</section>
{deepseek_section}
{gap_section}
<section>
    <h2>\u6280\u672f\u8bf4\u660e</h2>
    <ul>
        <li>trace_parser \u53ef\u7528\uff1a{'\u2705' if _TP_AVAILABLE else '\u274c\uff08\u56de\u9000\u5230\u6d88\u606f\u8ba1\u6570\u4ee3\u7406\uff09'}</li>
        <li>final_report.json: <code>{result.get('minicpm5',{}).get('_report_path','\u2014')}</code></li>
        <li>trace_dir: <code>{result.get('minicpm5',{}).get('_trace_dir','\u2014')}</code></li>
    </ul>
    <p><small>\u26a0\ufe0f \u9996\u6b21\u4f7f\u7528 MiniCPM5-2B \u4fa7\u771f\u5b9e\u8f68\u8ff9\u6570\u636e\u66ff\u4ee3\u4e4b\u524d\u7684\u5047\u8bbe\u5916\u63a8\u3002gap \u5206\u6790\u4e3a\u542f\u53d1\u5f0f\u4f30\u8ba1\uff0c\u975e\u7cbe\u786e\u5206\u89e3\u3002</small></p>
</section>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="R55: Automated Post-Baseline D1-D6 Analysis Pipeline"
    )
    parser.add_argument("--report-json", required=True, help="Path to final_report.json from the baseline run")
    parser.add_argument("--trace-dir", help="Path to cline_cli_trace/<version>/cline_trace/ directory")
    parser.add_argument("--dataset-jsonl", help="Path to EDA-Eval-PyAether-v20260311.jsonl")
    parser.add_argument("--deepseek-report-json", help="Path to DeepSeek side final_report.json")
    parser.add_argument("--deepseek-trace-dir", help="Path to DeepSeek side trace directory")
    parser.add_argument("--html", help="Path to output HTML report")
    parser.add_argument("--json-out", help="Path to output JSON summary (default: stdout)")
    args = parser.parse_args()

    dataset_meta = load_dataset(args.dataset_jsonl)
    dataset_path = args.dataset_jsonl or DEFAULT_DATASET

    m_report = load_report(args.report_json)
    if not m_report:
        print(f"ERROR: Cannot load report from {args.report_json}", file=sys.stderr)
        sys.exit(1)

    m_from_report = extract_from_report(m_report, dataset_meta)
    m_from_report["_report_path"] = os.path.abspath(args.report_json)
    m_from_report["_trace_dir"] = os.path.abspath(args.trace_dir) if args.trace_dir else None

    m_trace_dirs = find_trace_dirs(args.trace_dir) if args.trace_dir else []
    m_from_traces = extract_from_traces(m_trace_dirs)
    m_from_report["trace_analysis"] = m_from_traces

    d_from_report = None
    if args.deepseek_report_json:
        d_report = load_report(args.deepseek_report_json)
        if d_report:
            d_from_report = extract_from_report(d_report, dataset_meta)
            d_from_report["_report_path"] = os.path.abspath(args.deepseek_report_json)
            d_from_report["_trace_dir"] = os.path.abspath(args.deepseek_trace_dir) if args.deepseek_trace_dir else None
            d_trace_dirs = find_trace_dirs(args.deepseek_trace_dir) if args.deepseek_trace_dir else find_trace_dirs(DEFAULT_DEEPSEEK_TRACE)
            d_from_report["trace_analysis"] = extract_from_traces(d_trace_dirs)

    comparison = compare_sides(m_from_report, d_from_report)

    result = {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "minicpm5": m_from_report,
        "deepseek": d_from_report,
        "comparison": comparison,
        "_dataset_path": dataset_path,
    }

    json_str = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    if args.json_out:
        os.makedirs(os.path.dirname(args.json_out) or ".", exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"JSON summary written to {args.json_out}", file=sys.stderr)
    else:
        print(json_str)

    if args.html:
        generate_html(result, args.html)
        print(f"HTML report written to {args.html}", file=sys.stderr)

    print(f"\n=== D1-D6 Summary ===", file=sys.stderr)
    print(f"Model: {m_from_report.get('model_name','?')}", file=sys.stderr)
    print(f"Pass rate: {m_from_report.get('overall_pass_rate',0)*100:.1f}%", file=sys.stderr)
    print(f"D1 legality: {m_from_traces.get('D1_tool_call_legality','-')}", file=sys.stderr)
    print(f"D2 avg calls: {m_from_traces.get('D2_avg_calls_per_task','-')}", file=sys.stderr)
    print(f"D3 timeout: {m_from_report.get('D3_timeout_ratio',0)*100:.1f}%", file=sys.stderr)
    print(f"D6 avg iterations: {m_from_traces.get('D6_avg_iterations','-')}", file=sys.stderr)
    if comparison.get("gap_pp"):
        print(f"Gap vs DeepSeek: {comparison['gap_pp']} pp", file=sys.stderr)
        ga = comparison.get("gap_analysis", {})
        if ga:
            print(f"  Protocol-recoverable: ~{ga.get('protocol_recoverable_estimate_pp','-')} pp", file=sys.stderr)
            print(f"  Real capability gap: ~{ga.get('real_capability_gap_estimate_pp','-')} pp", file=sys.stderr)

if __name__ == "__main__":
    main()
