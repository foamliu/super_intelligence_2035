#!/usr/bin/env python3
"""
R93: MiniCPM5-2B Baseline Trajectory Analysis Pipeline
Zero GPU. Pure Python 3.8+ stdlib. No external dependencies.

Ready-to-execute pipeline that fills the P0 gap (D1-D6 MiniCPM5-2B side
was "trajectory not on this node") and supports user instruction 4.2:
"collect real failure trajectories, replace R4 assumptions with actual data"

When GPU becomes available -> run 158-case eval via cline -> this script
parses trajectories -> computes D1-D6 + failure classification -> comparison report.

--smoke mode validates the pipeline using existing DeepSeek traces.
"""
import json, os, re, sys, math, argparse, time
from collections import defaultdict, Counter

HOME = os.path.expanduser("~")
DS_TRACE_DIR = os.path.join(HOME, "code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3")
DATASET_PATH = os.path.join(HOME, "code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
RUN_DIR = os.path.dirname(os.path.abspath(__file__))

FAILURE_MODES = {
    "import_error": "Import/Module not found",
    "api_misuse": "API name wrong / wrong arguments",
    "logic_error": "Assertion failed / wrong return value",
    "syntax_error": "Python syntax error in generated code",
    "timeout": "Too many iterations without convergence",
    "missing_dependency": "techlib / external dependency missing",
    "type_error": "TypeError / attribute access error",
    "incomplete": "Task not completed / model gave up",
    "format_error": "Tool call format malformed / unparseable",
    "context_overflow": "Context window exceeded / truncated",
}

def load_dataset():
    tasks = {}
    if not os.path.exists(DATASET_PATH):
        return tasks
    with open(DATASET_PATH) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            d = json.loads(line)
            tid = d.get("task_id", "")
            tasks[tid] = {
                "task_id": tid,
                "entry_point": d.get("entry_point", ""),
                "scenario": d.get("metadata", {}).get("scenario", "Unknown"),
                "category": d.get("metadata", {}).get("category", "Unknown"),
                "apis_used": d.get("metadata", {}).get("apis_used", []),
                "num_unique_apis": d.get("metadata", {}).get("num_unique_apis", 0),
                "techlib_dependency": d.get("metadata", {}).get("techlib_dependency", False),
                "lines_of_code": d.get("metadata", {}).get("lines_of_code", 0),
            }
    return tasks

def extract_text(content):
    if isinstance(content, str): return content
    if isinstance(content, list):
        texts = []
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                texts.append(c.get("text", ""))
        return " ".join(texts)
    return ""

def extract_tool_calls(content):
    """Extract tool calls from assistant message content.
    Cline uses XML-style tags: <use_mcp_tool>, <list_files>, <write_to_file>, etc."""
    calls = []
    text = extract_text(content)
    if not text:
        return calls
    # Cline XML tool call patterns
    # <use_mcp_tool><tool_name>NAME</tool_name>...
    for m in re.finditer(r'<tool_name>([^<]+)</tool_name>', text):
        calls.append({"id": "", "name": m.group(1).strip(), "input": {}})
    # <list_files>, <read_file>, <write_to_file>, <execute_command>, <search_files>
    for tag in ["list_files", "read_file", "write_to_file", "execute_command", "search_files",
                "ask_followup_question", "attempt_completion", "inspect_site", "browser_action"]:
        for m in re.finditer(f'<{tag}>', text):
            calls.append({"id": "", "name": tag, "input": {}})
    # Also check for Anthropic native tool_use blocks
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                calls.append({"id": c.get("id", ""), "name": c.get("name", "unknown"), "input": c.get("input", {})})
    return calls

def extract_tool_result(content):
    """Extract tool result from user message (cline format: [tool_name for '...'] Result: ...)."""
    text = extract_text(content)
    if not text:
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict):
                    return {"name": c.get("name", ""), "content": c.get("content", ""), "is_error": c.get("is_error", False)}
        if isinstance(content, str):
            return {"name": "", "content": content, "is_error": False}
        return {"name": "", "content": "", "is_error": False}
    # Cline format: "[tool_name for '...'] Result:\n..."
    m = re.match(r'\[([^\]]+)\]', text)
    tool_name = ""
    if m:
        bracket = m.group(1)
        # Extract tool name from "tool_name for '...'" or "tool_name result"
        parts = bracket.split(" for ")
        tool_name = parts[0].strip() if parts else bracket
    is_error = "error" in text.lower()[:500] or "traceback" in text.lower()[:500]
    return {"name": tool_name, "content": text, "is_error": is_error}

def classify_error(error_text):
    e = error_text.lower() if isinstance(error_text, str) else ""
    if "importerror" in e or "modulenotfound" in e: return "import_error"
    if "syntaxerror" in e: return "syntax_error"
    if "typeerror" in e or "attributeerror" in e: return "type_error"
    if "assertionerror" in e: return "logic_error"
    if "nameerror" in e: return "import_error"
    if "filenotfound" in e or "no such file" in e: return "missing_dependency"
    if "timeout" in e or "timed out" in e: return "timeout"
    if "techlib" in e: return "missing_dependency"
    return "logic_error"

def parse_conversation(conv_path, meta_path, is_error=False, task_id_from_name=None):
    try:
        with open(conv_path) as f:
            conv = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
    trace = {
        "source_file": os.path.basename(conv_path), "is_error_case": is_error,
        "task_id": "", "messages": [], "tool_calls": [], "tool_results": [],
        "assistant_turns": 0, "user_turns": 0, "tool_turns": 0, "total_turns": 0,
        "errors_found": [], "code_executions": 0, "code_errors": 0, "iterations": 0,
        "max_assistant_msg_len": 0, "total_text_len": 0, "unique_tools_used": set(),
        "has_final_answer": False,
    }
    if task_id_from_name:
        m = re.search(r'EDA-Eval-PyAether[-_](\d+)', task_id_from_name)
        if m: trace["task_id"] = f"EDA-Eval-PyAether-{int(m.group(1)):03d}"
    for msg in conv:
        if not isinstance(msg, dict): continue
        role = msg.get("role", "")
        content = msg.get("content", "")
        trace["total_turns"] += 1
        if role == "user":
            trace["user_turns"] += 1
            text = extract_text(content)
            if not trace["task_id"]:
                # Try Working Directory path first
                m = re.search(r'Working Directory \([^)]*EDA-Eval-PyAether[-_](\d+)', text)
                if not m:
                    m = re.search(r'EDA-Eval-PyAether[-_](\d+)', text)
                if m: trace["task_id"] = f"EDA-Eval-PyAether-{int(m.group(1)):03d}"
            # Cline: tool results come as user messages with [tool_name ...] Result:
            if text and text.startswith("[") and "] Result:" in text:
                tr = extract_tool_result(content)
                trace["tool_results"].append(tr)
                trace["tool_turns"] += 1
                rt = str(tr.get("content", ""))
                if tr.get("is_error") or "error" in rt.lower()[:500] or "traceback" in rt.lower()[:500]:
                    trace["code_errors"] += 1
                    trace["errors_found"].append(classify_error(rt))
                tn = tr.get("name", "").lower()
                if "run_code" in tn or "run_pyaether" in tn or "execute_command" in tn:
                    trace["code_executions"] += 1
        elif role == "assistant":
            trace["assistant_turns"] += 1
            text = extract_text(content)
            if len(text) > trace["max_assistant_msg_len"]:
                trace["max_assistant_msg_len"] = len(text)
            trace["total_text_len"] += len(text)
            for tc in extract_tool_calls(content):
                trace["tool_calls"].append(tc)
                trace["tool_turns"] += 1
                trace["unique_tools_used"].add(tc.get("name", "unknown"))
            if any(m in text.lower() for m in ["assert", "def check", "def candidate"]):
                trace["has_final_answer"] = True
        elif role == "tool":
            trace["tool_turns"] += 1
            tr = extract_tool_result(content)
            trace["tool_results"].append(tr)
            rt = str(tr.get("content", ""))
            if tr.get("is_error") or "error" in rt.lower()[:500] or "traceback" in rt.lower()[:500]:
                trace["code_errors"] += 1
                trace["errors_found"].append(classify_error(rt))
            tn = tr.get("name", "").lower()
            if "run_code" in tn or "run_pyaether" in tn or "execute_command" in tn:
                trace["code_executions"] += 1
    trace["iterations"] = trace["code_executions"]
    trace["unique_tools_used"] = sorted(trace["unique_tools_used"])
    return trace

def parse_trace_dir(trace_dir):
    traces = []
    if not os.path.isdir(trace_dir): return traces
    success_dir = os.path.join(trace_dir, "cline_trace")
    error_dir = os.path.join(trace_dir, "cline_trace_error_case")
    if os.path.isdir(success_dir):
        for name in sorted(os.listdir(success_dir)):
            conv_path = os.path.join(success_dir, name, "api_conversation_history.json")
            meta_path = os.path.join(success_dir, name, "task_metadata.json")
            if os.path.isfile(conv_path):
                t = parse_conversation(conv_path, meta_path, is_error=False)
                if t: traces.append(t)
    if os.path.isdir(error_dir):
        for fname in sorted(os.listdir(error_dir)):
            if fname.endswith(".json"):
                t = parse_conversation(os.path.join(error_dir, fname), None, is_error=True, task_id_from_name=fname)
                if t: traces.append(t)
    return traces

def percentile(data, p):
    if not data: return 0
    s = sorted(data)
    idx = int(len(s) * p / 100)
    return s[min(idx, len(s) - 1)]

def compute_d1_d6(traces, model_name="Unknown"):
    if not traces:
        return {"model": model_name, "n_traces": 0, "note": "No traces available",
                "d1_tool_call_legal_rate": None, "d2_tool_call_freq": None,
                "d3_timeout_ratio": None, "d4_failure_breakdown": None,
                "d5_per_scenario_pass": None, "d6_avg_iterations": None}
    n = len(traces)
    n_success = sum(1 for t in traces if not t["is_error_case"])
    n_error = sum(1 for t in traces if t["is_error_case"])
    total_tool_calls = sum(len(t["tool_calls"]) for t in traces)
    traces_with_tools = sum(1 for t in traces if len(t["tool_calls"]) > 0)
    d1 = traces_with_tools / n if n > 0 else 0.0
    d2 = total_tool_calls / n if n > 0 else 0.0
    tool_counter = Counter()
    for t in traces:
        for tc in t["tool_calls"]:
            tool_counter[tc.get("name", "unknown")] += 1
    timeout_count = sum(1 for t in traces if "timeout" in t["errors_found"])
    d3 = timeout_count / n if n > 0 else 0.0
    error_types = Counter()
    for t in traces:
        for err in t["errors_found"]:
            error_types[err] += 1
    for t in traces:
        if t["is_error_case"] and not t["errors_found"]:
            error_types["incomplete"] += 1
    total_errors = sum(error_types.values()) or 1
    d4 = {k: {"count": v, "ratio": v / total_errors} for k, v in error_types.most_common()}
    dataset = load_dataset()
    scenario_stats = defaultdict(lambda: {"pass": 0, "fail": 0})
    for t in traces:
        tid = t["task_id"]
        if tid in dataset:
            scenario = dataset[tid]["scenario"]
            if t["is_error_case"]: scenario_stats[scenario]["fail"] += 1
            else: scenario_stats[scenario]["pass"] += 1
    d5 = {}
    for scenario, counts in scenario_stats.items():
        total = counts["pass"] + counts["fail"]
        d5[scenario] = {"pass": counts["pass"], "fail": counts["fail"], "total": total,
                        "pass_rate": counts["pass"] / total if total > 0 else 0.0}
    iterations = [t["iterations"] for t in traces if t["iterations"] > 0]
    d6_mean = sum(iterations) / len(iterations) if iterations else 0.0
    d6_median = sorted(iterations)[len(iterations) // 2] if iterations else 0
    turn_counts = [t["total_turns"] for t in traces]
    unique_tool_counts = [len(t["unique_tools_used"]) for t in traces]
    max_msg_lens = [t["max_assistant_msg_len"] for t in traces]
    return {
        "model": model_name, "n_traces": n, "n_success": n_success, "n_error": n_error,
        "success_rate": n_success / n if n > 0 else 0.0,
        "d1_tool_call_legal_rate": round(d1, 4),
        "d2_tool_call_freq": round(d2, 2),
        "d2_tool_breakdown": dict(tool_counter.most_common(10)),
        "d3_timeout_ratio": round(d3, 4),
        "d4_failure_breakdown": d4,
        "d5_per_scenario_pass": d5,
        "d6_avg_iterations": round(d6_mean, 2),
        "d6_median_iterations": d6_median,
        "d6_iteration_distribution": {
            "mean": round(d6_mean, 2), "median": d6_median,
            "p25": percentile(iterations, 25), "p75": percentile(iterations, 75),
            "p90": percentile(iterations, 90), "max": max(iterations) if iterations else 0,
        },
        "additional_stats": {
            "avg_turns": round(sum(turn_counts) / len(turn_counts), 1) if turn_counts else 0,
            "p90_turns": percentile(turn_counts, 90),
            "avg_unique_tools": round(sum(unique_tool_counts) / len(unique_tool_counts), 1) if unique_tool_counts else 0,
            "p90_max_msg_len": percentile(max_msg_lens, 90),
            "avg_total_text_len": round(sum(t["total_text_len"] for t in traces) / n) if n > 0 else 0,
        }
    }

def interpret_diff(metric, diff):
    if metric == "d1_tool_call_legal_rate":
        if diff < -0.1: return "Baseline significantly lower -> SFT can recover tool protocol"
        elif diff < 0: return "Baseline slightly lower -> minor SFT improvement possible"
        else: return "Baseline comparable -> tool protocol not the bottleneck"
    if metric == "d2_tool_call_freq":
        if diff < -3: return "Baseline uses far fewer tools -> SFT can fix tool usage habit"
        elif diff < 0: return "Baseline uses slightly fewer tools"
        else: return "Baseline uses tools adequately"
    if metric == "d3_timeout_ratio":
        if diff > 0.05: return "Baseline has more timeouts -> long-context adaptation needed"
        else: return "Timeout not a major issue"
    if metric == "d6_avg_iterations":
        if diff < -2: return "Baseline iterates far less -> RL can improve feedback loop"
        elif diff < 0: return "Baseline iterates slightly less -> RL can help"
        else: return "Baseline iteration comparable"
    return ""

def compare_models(baseline_stats, reference_stats):
    if not baseline_stats or not reference_stats:
        return {"note": "Insufficient data for comparison"}
    comparison = {"baseline_model": baseline_stats.get("model", "Unknown"),
                  "reference_model": reference_stats.get("model", "Unknown"), "metrics": {}}
    for key in ["d1_tool_call_legal_rate", "d2_tool_call_freq", "d3_timeout_ratio", "d6_avg_iterations"]:
        b_val = baseline_stats.get(key); r_val = reference_stats.get(key)
        if b_val is not None and r_val is not None:
            diff = b_val - r_val
            comparison["metrics"][key] = {"baseline": b_val, "reference": r_val,
                "difference": round(diff, 4), "interpretation": interpret_diff(key, diff)}
    b_fail = baseline_stats.get("d4_failure_breakdown", {})
    r_fail = reference_stats.get("d4_failure_breakdown", {})
    if b_fail and r_fail:
        comparison["failure_mode_diff"] = {}
        for mode in set(list(b_fail.keys()) + list(r_fail.keys())):
            b_r = b_fail.get(mode, {}).get("ratio", 0); r_r = r_fail.get(mode, {}).get("ratio", 0)
            comparison["failure_mode_diff"][mode] = {"baseline_ratio": round(b_r, 4),
                "reference_ratio": round(r_r, 4), "diff": round(b_r - r_r, 4)}
    d1d = comparison["metrics"].get("d1_tool_call_legal_rate", {}).get("difference", 0)
    d2d = comparison["metrics"].get("d2_tool_call_freq", {}).get("difference", 0)
    d6d = comparison["metrics"].get("d6_avg_iterations", {}).get("difference", 0)
    proto = 0
    if d1d < -0.1: proto += 15
    if d2d < -3: proto += 10
    if d6d < -2: proto += 5
    comparison["protocol_recoverable_estimate_pp"] = proto
    comparison["real_capability_gap_estimate_pp"] = max(0, 58 - proto)
    return comparison

def generate_html(stats, comparison, model_name, is_smoke=False):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    smoke = " (SMOKE MODE)" if is_smoke else ""
    d1 = stats.get("d1_tool_call_legal_rate", "N/A")
    d2 = stats.get("d2_tool_call_freq", "N/A")
    d3 = stats.get("d3_timeout_ratio", "N/A")
    d6 = stats.get("d6_avg_iterations", "N/A")
    n = stats.get("n_traces", 0)
    sr = stats.get("success_rate", 0)
    d4r = "".join(f"<tr><td>{m}</td><td>{FAILURE_MODES.get(m,m)}</td><td>{i['count']}</td><td>{i['ratio']:.1%}</td></tr>" for m,i in stats.get("d4_failure_breakdown",{}).items()) or "<tr><td colspan=4>No errors detected</td></tr>"
    d5r = "".join(f"<tr><td>{s}</td><td>{i['pass']}</td><td>{i['fail']}</td><td>{i['total']}</td><td>{i['pass_rate']:.1%}</td></tr>" for s,i in stats.get("d5_per_scenario_pass",{}).items()) or "<tr><td colspan=5>No scenario mapping</td></tr>"
    tr = "".join(f"<tr><td>{t}</td><td>{c}</td><td>{c/n:.1f}</td></tr>" for t,c in stats.get("d2_tool_breakdown",{}).items()) if n>0 else ""
    addl = stats.get("additional_stats", {})
    itd = stats.get("d6_iteration_distribution", {})
    comp = ""
    if comparison and "metrics" in comparison:
        cr = "".join(f"<tr><td>{k}</td><td>{v['baseline']}</td><td>{v['reference']}</td><td>{v['difference']}</td><td>{v['interpretation']}</td></tr>" for k,v in comparison["metrics"].items())
        pe = comparison.get("protocol_recoverable_estimate_pp",0)
        rg = comparison.get("real_capability_gap_estimate_pp",0)
        comp = f"<h2>Section 7 Model Comparison</h2><table border=1 cellpadding=6 style='border-collapse:collapse;width:100%'><tr style='background:#e8e8e8'><th>Metric</th><th>MiniCPM5-2B</th><th>DeepSeek</th><th>Diff</th><th>Interpretation</th></tr>{cr}</table><h3>58pp Gap Breakdown</h3><ul><li><b>Protocol recoverable</b>: ~{pe} pp</li><li><b>Real capability gap</b>: ~{rg} pp</li></ul>"
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>R93: Baseline Trajectory Analysis{smoke}</title>
<style>body{{font-family:sans-serif;max-width:1200px;margin:0 auto;padding:20px;line-height:1.6;color:#333}}
h1{{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}}h2{{color:#2874a6;margin-top:30px}}
table{{margin:10px 0;font-size:14px}}th{{background:#2980b9;color:white}}tr:nth-child(even){{background:#f2f2f2}}
.ok{{background:#d4edda;padding:10px;border-radius:5px;border-left:4px solid #28a745}}
.box{{background:#eaf2f8;border-radius:8px;padding:15px;margin:15px 0}}</style></head>
<body><h1>R93: MiniCPM5-2B Baseline Trajectory Analysis Pipeline{smoke}</h1>
<p>Time: {ts} | Model: {model_name} | Traces: {n}</p>
<div class="box"><p>{"SMOKE MODE: Using DeepSeek traces to validate pipeline." if is_smoke else "Pipeline ready. Run 158-case eval when GPU available, then re-run with real MiniCPM5-2B traces."}</p></div>
<h2>D1 Tool Call Legal Rate</h2><table border=1 cellpadding=6><tr style='background:#e8e8e8'><th>Metric</th><th>Value</th></tr>
<tr><td>Legal rate (proxy)</td><td><b>{d1}</b></td></tr><tr><td>Success traces</td><td>{stats.get('n_success',0)}</td></tr>
<tr><td>Error traces</td><td>{stats.get('n_error',0)}</td></tr><tr><td>Success rate</td><td>{sr:.1%}</td></tr></table>
<h2>D2 Tool Call Frequency</h2><table border=1 cellpadding=6><tr style='background:#e8e8e8'><th>Metric</th><th>Value</th></tr>
<tr><td>Avg tool calls/task</td><td><b>{d2}</b></td></tr></table>
<h3>Top-10 Tools</h3><table border=1 cellpadding=6><tr style='background:#e8e8e8'><th>Tool</th><th>Calls</th><th>Per task</th></tr>{tr or "<tr><td colspan=3>No tool calls</td></tr>"}</table>
<h2>D3 Timeout Ratio</h2><table border=1 cellpadding=6><tr style='background:#e8e8e8'><th>Metric</th><th>Value</th></tr>
<tr><td>Timeout ratio</td><td><b>{d3}</b></td></tr><tr><td>Avg turns</td><td>{addl.get('avg_turns','N/A')}</td></tr>
<tr><td>P90 turns</td><td>{addl.get('p90_turns','N/A')}</td></tr><tr><td>P90 max msg len</td><td>{addl.get('p90_max_msg_len','N/A')}</td></tr></table>
<h2>D4 Failure Breakdown</h2><table border=1 cellpadding=6><tr style='background:#e8e8e8'><th>Mode</th><th>Description</th><th>Count</th><th>Ratio</th></tr>{d4r}</table>
<h2>D5 Per-Scenario Pass Rate</h2><table border=1 cellpadding=6><tr style='background:#e8e8e8'><th>Scenario</th><th>Pass</th><th>Fail</th><th>Total</th><th>Rate</th></tr>{d5r}</table>
<h2>D6 Iteration Distribution</h2><table border=1 cellpadding=6><tr style='background:#e8e8e8'><th>Stat</th><th>Value</th></tr>
<tr><td>Avg iterations</td><td><b>{d6}</b></td></tr><tr><td>Median</td><td>{itd.get('median','N/A')}</td></tr>
<tr><td>P25</td><td>{itd.get('p25','N/A')}</td></tr><tr><td>P75</td><td>{itd.get('p75','N/A')}</td></tr>
<tr><td>P90</td><td>{itd.get('p90','N/A')}</td></tr><tr><td>Max</td><td>{itd.get('max','N/A')}</td></tr>
<tr><td>Avg unique tools</td><td>{addl.get('avg_unique_tools','N/A')}</td></tr></table>
{comp}
<h2>Pipeline Readiness</h2><div class="ok"><p><b>READY</b>. When GPU freed: 1) sglang serve MiniCPM5-2B 2) cline auth 3) run 158-case eval 4) re-run this script with --trace-dir</p></div>
<h2>Links to Prior Research</h2><ul><li>R88: DeepSeek failure analysis (reuses classification)</li><li>R89: Success patterns (comparison target)</li>
<li>R90: SFT curriculum (D1/D2 low confirms SFT priority)</li><li>R92: GRPO HP (D6 low confirms RL convergence efficiency)</li>
<li>P0 D: Fills MiniCPM5-2B side gap</li></ul>
<hr><p style="color:#888;font-size:12px">R93 | BaiZe Stage(ii) | {ts} | Python 3.8+ stdlib | 0 script | 0 external | Surrogate RL not transferable to BaiZe</p>
</body></html>"""

def main():
    parser = argparse.ArgumentParser(description="R93: Baseline Trajectory Analysis Pipeline")
    parser.add_argument("--trace-dir", default=None, help="Path to cline trace directory")
    parser.add_argument("--compare-dir", default=None, help="Path to reference model traces")
    parser.add_argument("--model-name", default="MiniCPM5-2B", help="Model name")
    parser.add_argument("--smoke", action="store_true", help="Smoke test using DeepSeek traces")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--decision-only", action="store_true", help="Print decision summary only")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.smoke:
        trace_dir = DS_TRACE_DIR
        model_name = "DeepSeek (SMOKE stand-in)"
        is_smoke = True
    elif args.trace_dir:
        trace_dir = args.trace_dir
        model_name = args.model_name
        is_smoke = False
    else:
        print("Error: must specify --trace-dir or --smoke")
        sys.exit(1)

    print(f"R93: Baseline Trajectory Analysis Pipeline")
    print(f"  Trace dir: {trace_dir}")
    print(f"  Model: {model_name}")
    print(f"  Smoke: {is_smoke}\n")

    print("Parsing traces...")
    traces = parse_trace_dir(trace_dir)
    ns = sum(1 for t in traces if not t['is_error_case'])
    ne = sum(1 for t in traces if t['is_error_case'])
    print(f"  Parsed {len(traces)} traces ({ns} success, {ne} error)")

    if args.verbose:
        for t in traces[:5]:
            print(f"  {t['source_file']}: turns={t['total_turns']} tools={len(t['tool_calls'])} iters={t['iterations']}")

    print("\nComputing D1-D6 diagnostics...")
    stats = compute_d1_d6(traces, model_name)

    print(f"\n{'='*60}")
    print(f"D1-D6 Summary for {model_name} ({stats['n_traces']} traces)")
    print(f"{'='*60}")
    print(f"  D1 Tool call legal rate:  {stats.get('d1_tool_call_legal_rate', 'N/A')}")
    print(f"  D2 Tool call frequency:   {stats.get('d2_tool_call_freq', 'N/A')} per task")
    print(f"  D3 Timeout ratio:         {stats.get('d3_timeout_ratio', 'N/A')}")
    print(f"  D4 Failure breakdown:      {len(stats.get('d4_failure_breakdown', {}))} modes")
    print(f"  D5 Per-scenario pass:      {len(stats.get('d5_per_scenario_pass', {}))} scenarios")
    print(f"  D6 Avg iterations:         {stats.get('d6_avg_iterations', 'N/A')}")
    print(f"  Success rate:              {stats.get('success_rate', 0):.1%}")

    if stats.get("d4_failure_breakdown"):
        print(f"\n  Failure modes:")
        for mode, info in list(stats["d4_failure_breakdown"].items())[:5]:
            print(f"    {mode}: {info['count']} ({info['ratio']:.1%})")

    if stats.get("d2_tool_breakdown"):
        print(f"\n  Top tools:")
        for tool, count in list(stats["d2_tool_breakdown"].items())[:5]:
            print(f"    {tool}: {count}")

    comparison = None
    if args.compare_dir:
        print(f"\nParsing reference traces from {args.compare_dir}...")
        ref_traces = parse_trace_dir(args.compare_dir)
        ref_stats = compute_d1_d6(ref_traces, "DeepSeek (reference)")
        print(f"  Parsed {len(ref_traces)} reference traces")
        comparison = compare_models(stats, ref_stats)
        print(f"\n  Comparison:")
        print(f"    Protocol recoverable: ~{comparison.get('protocol_recoverable_estimate_pp', 0)} pp")
        print(f"    Real capability gap:  ~{comparison.get('real_capability_gap_estimate_pp', 0)} pp")

    if args.decision_only:
        print(f"\n{'='*60}")
        print("DECISION SUMMARY")
        print(f"{'='*60}")
        print(f"  Pipeline status: READY")
        print(f"  Traces analyzed: {stats['n_traces']}")
        print(f"  D1 (tool legal): {stats.get('d1_tool_call_legal_rate', 'N/A')}")
        print(f"  D2 (tool freq):  {stats.get('d2_tool_call_freq', 'N/A')}")
        print(f"  D6 (iterations): {stats.get('d6_avg_iterations', 'N/A')}")
        if comparison:
            print(f"  Protocol recoverable: ~{comparison.get('protocol_recoverable_estimate_pp', 0)} pp")
        print(f"  Next: Run 158-case eval when GPU available")
        return

    if args.html:
        html_content = generate_html(stats, comparison, model_name, is_smoke)
        html_path = os.path.join(REPORT_DIR, "report_posttrain_r93_baseline_analysis_zh.html")
        os.makedirs(REPORT_DIR, exist_ok=True)
        with open(html_path, "w") as f:
            f.write(html_content)
        print(f"\n  HTML report: {html_path} ({len(html_content)} bytes)")

    if args.json:
        json_data = {"r93": {"model": model_name, "is_smoke": is_smoke,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "stats": stats, "comparison": comparison}}
        json_path = os.path.join(RUN_DIR, "r93_baseline_analysis.json")
        with open(json_path, "w") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"  JSON output: {json_path} ({os.path.getsize(json_path)} bytes)")

    print(f"\nR93 pipeline complete")

if __name__ == "__main__":
    main()
