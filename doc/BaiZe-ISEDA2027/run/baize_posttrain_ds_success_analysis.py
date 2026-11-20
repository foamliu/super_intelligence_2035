#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R89: DeepSeek Success Trace Pattern Mining — SFT Positive Curriculum Design
         & API Usage Pattern Analysis (winning patterns from 83 successful traces)

Complement to R88 (which analyzed 20 failures). R89 mines the 83 SUCCESSFUL
DeepSeek full-harness traces to extract winning patterns for SFT curriculum.
Zero GPU. Pure Python 3.8+ stdlib. No external dependencies.
"""
import json, os, re, sys, math, time
from collections import defaultdict, Counter

HOME = os.path.expanduser("~")
TRACE_DIR = os.path.join(HOME, "code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace")
ERROR_CASE_DIR = os.path.join(HOME, "code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace_error_case")
DATASET_PATH = os.path.join(HOME, "code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
RUN_DIR = os.path.dirname(__file__)

def load_dataset():
    tasks = {}
    with open(DATASET_PATH) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            d = json.loads(line)
            tid = d["task_id"]
            tasks[tid] = {
                "task_id": tid, "entry_point": d.get("entry_point", ""),
                "scenario": d.get("metadata", {}).get("scenario", "Unknown"),
                "category": d.get("metadata", {}).get("category", "Unknown"),
                "apis_used": d.get("metadata", {}).get("apis_used", []),
                "num_unique_apis": d.get("metadata", {}).get("num_unique_apis", 0),
                "techlib_dependency": d.get("metadata", {}).get("techlib_dependency", False),
                "lines_of_code": d.get("metadata", {}).get("lines_of_code", 0),
                "task_name": d.get("metadata", {}).get("task_name", ""),
            }
    return tasks

def extract_entry_point(conv):
    for msg in conv:
        if not isinstance(msg, dict): continue
        if msg.get("role") != "user": continue
        content = msg.get("content", "")
        texts = []
        if isinstance(content, list):
            texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
        elif isinstance(content, str): texts = [content]
        for text in texts:
            m = re.search(r"def\s+(\w+)\s*\(", text)
            if m: return m.group(1)
    return None

def extract_error_case_ids():
    error_ids = set()
    if not os.path.isdir(ERROR_CASE_DIR): return error_ids
    for fname in os.listdir(ERROR_CASE_DIR):
        if not fname.endswith(".json"): continue
        m = re.search(r"EDA-Eval-PyAether[_-](\d+)", fname)
        if m: error_ids.add(f"EDA-Eval-PyAether-{int(m.group(1)):03d}")
    return error_ids

def extract_all_text(msg):
    content = msg.get("content", "")
    texts = []
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text": texts.append(b.get("text", ""))
    elif isinstance(content, str): texts.append(content)
    return texts

TOOL_CALL_RE = re.compile(r"<(use_mcp_tool|write_to_file|read_file|list_files|execute_command|search_files|ask_followup_question|attempt_completion)\b", re.IGNORECASE)
TOOL_RESULT_RE = re.compile(r"\[(use_mcp_tool|write_to_file|read_file|list_files|execute_command|search_files|ask_followup_question|attempt_completion)\s+for\s+'?([^'\]]+)'?\]", re.IGNORECASE)
MCP_TOOL_NAME_RE = re.compile(r"<tool_name>(\w+)</tool_name>", re.IGNORECASE)

def extract_tool_calls(conv):
    calls = []
    for idx, msg in enumerate(conv):
        if not isinstance(msg, dict): continue
        texts = extract_all_text(msg)
        full_text = "\n".join(texts)
        role = msg.get("role", "")
        if role == "assistant":
            for m in TOOL_CALL_RE.finditer(full_text):
                tool_tag = m.group(1).lower()
                tool_name = None
                if tool_tag == "use_mcp_tool":
                    m2 = MCP_TOOL_NAME_RE.search(full_text[m.start():m.start()+500])
                    if m2: tool_name = m2.group(1)
                calls.append({"idx": idx, "role": "assistant", "tool": tool_tag, "mcp_tool": tool_name})
        elif role == "user":
            for m in TOOL_RESULT_RE.finditer(full_text):
                calls.append({"idx": idx, "role": "user", "tool": m.group(1).lower()+"_result", "server": m.group(2).strip()})
    return calls

def extract_code_blocks(conv):
    code_blocks = []
    for idx, msg in enumerate(conv):
        if not isinstance(msg, dict): continue
        texts = extract_all_text(msg)
        full_text = "\n".join(texts)
        if msg.get("role") != "assistant": continue
        for m in re.finditer(r"<write_to_file>\s*<path>([^<]+)</path>\s*<content>(.*?)</content>", full_text, re.DOTALL):
            content = m.group(2)
            code_blocks.append({"idx": idx, "tool": "write_to_file", "lines": len(content.strip().split("\n"))})
        for m in re.finditer(r"<execute_command>\s*<command>(.*?)</command>", full_text, re.DOTALL):
            code_blocks.append({"idx": idx, "tool": "execute_command", "cmd": m.group(1).strip()[:200]})
    return code_blocks

def extract_error_signals(conv):
    signals = Counter()
    for msg in conv:
        texts = extract_all_text(msg)
        for text in texts:
            tl = text.lower()
            if "importerror" in tl or "modulenotfounderror" in tl: signals["import_error"] += 1
            if "attributeerror" in tl or "has no attribute" in tl: signals["attribute_error"] += 1
            if "nameerror" in tl or "is not defined" in tl: signals["name_error"] += 1
            if "typeerror" in tl: signals["type_error"] += 1
            if "assertionerror" in tl or ("assert" in tl and "fail" in tl): signals["assertion_error"] += 1
            if "syntaxerror" in tl or "invalid syntax" in tl: signals["syntax_error"] += 1
            if "traceback" in tl: signals["traceback"] += 1
    return signals

def extract_api_names_from_search(conv):
    searched_apis = []
    for msg in conv:
        texts = extract_all_text(msg)
        full_text = "\n".join(texts)
        if msg.get("role") == "user":
            for m in re.finditer(r'"api_name":\s*"([^"]+)"', full_text):
                searched_apis.append(m.group(1).split(":")[0].strip())
    return searched_apis

def measure_iteration_cycles(conv):
    code_actions = []
    for idx, msg in enumerate(conv):
        if not isinstance(msg, dict) or msg.get("role") != "assistant": continue
        texts = extract_all_text(msg)
        full_text = "\n".join(texts)
        if "<write_to_file>" in full_text or "<execute_command>" in full_text:
            code_actions.append(idx)
    error_msgs = []
    for idx, msg in enumerate(conv):
        if not isinstance(msg, dict) or msg.get("role") != "user": continue
        texts = extract_all_text(msg)
        for text in texts:
            if "traceback" in text.lower() or "error" in text.lower() or "exception" in text.lower():
                error_msgs.append(idx); break
    cycles = 0
    for i, ca_idx in enumerate(code_actions):
        next_ca = code_actions[i+1] if i+1 < len(code_actions) else float("inf")
        for em_idx in error_msgs:
            if ca_idx < em_idx < next_ca: cycles += 1; break
    return {"code_actions": len(code_actions), "error_messages": len(error_msgs), "fix_cycles": cycles}

def load_all_traces(dataset, error_ids):
    traces = []
    for dirname in sorted(os.listdir(TRACE_DIR)):
        conv_path = os.path.join(TRACE_DIR, dirname, "api_conversation_history.json")
        if not os.path.isfile(conv_path): continue
        try: conv = json.load(open(conv_path))
        except Exception: continue
        entry_point = extract_entry_point(conv)
        task_meta = None; tid = None
        for t, v in dataset.items():
            if v["entry_point"] == entry_point: task_meta = v; tid = t; break
        is_error = tid in error_ids if tid else False
        if not is_error and entry_point:
            for eid in error_ids:
                if eid in dataset and dataset[eid]["entry_point"] == entry_point: is_error = True; break
        traces.append({"dir": dirname, "task_id": tid, "entry_point": entry_point,
                       "task_meta": task_meta, "conv": conv, "conv_len": len(conv), "is_error": is_error})
    return traces

def analyze_trace(trace):
    conv = trace["conv"]
    calls = extract_tool_calls(conv)
    code_blocks = extract_code_blocks(conv)
    errors = extract_error_signals(conv)
    cycles = measure_iteration_cycles(conv)
    searched_apis = extract_api_names_from_search(conv)
    tool_freq = Counter(); mcp_tool_freq = Counter()
    for c in calls:
        if c["role"] == "assistant":
            tool_freq[c["tool"]] += 1
            if c.get("mcp_tool"): mcp_tool_freq[c["mcp_tool"]] += 1
    sequence = []
    for c in calls:
        if c["role"] == "assistant":
            sequence.append(c["mcp_tool"] if c["tool"] == "use_mcp_tool" and c.get("mcp_tool") else c["tool"])
    total_code_lines = sum(cb.get("lines", 0) for cb in code_blocks if cb.get("tool") == "write_to_file")
    first_search = first_detail = None
    for c in calls:
        if c["role"] == "assistant":
            if c.get("mcp_tool") == "search_apis" and first_search is None: first_search = c["idx"]
            if c.get("mcp_tool") == "get_api_details" and first_detail is None: first_detail = c["idx"]
    api_discovery_gap = (first_detail - first_search) if (first_search is not None and first_detail is not None) else None
    return {
        "conv_len": trace["conv_len"], "tool_calls_total": len([c for c in calls if c["role"]=="assistant"]),
        "tool_freq": dict(tool_freq), "mcp_tool_freq": dict(mcp_tool_freq),
        "sequence": sequence, "sequence_len": len(sequence), "code_blocks": len(code_blocks),
        "write_to_file_count": tool_freq.get("write_to_file", 0),
        "execute_command_count": tool_freq.get("execute_command", 0),
        "total_code_lines": total_code_lines, "error_signals": dict(errors),
        "has_errors": sum(errors.values()) > 0, "fix_cycles": cycles["fix_cycles"],
        "code_actions": cycles["code_actions"], "searched_apis": searched_apis,
        "unique_searched_apis": len(set(searched_apis)), "api_discovery_gap": api_discovery_gap,
        "search_apis_count": mcp_tool_freq.get("search_apis", 0),
        "get_api_details_count": mcp_tool_freq.get("get_api_details", 0),
    }

def extract_common_sequences(success_analyses, min_length=3, max_length=6):
    seq_counter = Counter()
    for a in success_analyses:
        seq = a["sequence"]
        for n in range(min_length, min(max_length+1, len(seq)+1)):
            for i in range(len(seq)-n+1):
                seq_counter[tuple(seq[i:i+n])] += 1
    return seq_counter

def compute_statistics(values):
    if not values: return {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "n": 0}
    n = len(values); mean = sum(values)/n; sorted_v = sorted(values)
    median = sorted_v[n//2] if n%2==1 else (sorted_v[n//2-1]+sorted_v[n//2])/2
    std = math.sqrt(sum((v-mean)**2 for v in values)/n)
    return {"mean": round(mean,2), "median": round(median,1), "std": round(std,2),
            "min": min(values), "max": max(values), "n": n}

def categorize_difficulty(task_meta):
    if not task_meta: return "Unknown"
    n_apis = task_meta.get("num_unique_apis", 0); loc = task_meta.get("lines_of_code", 0)
    if n_apis <= 2 and loc <= 5: return "L1_trivial"
    if n_apis <= 3 and loc <= 8: return "L2_easy"
    if n_apis <= 5 and loc <= 12: return "L3_medium"
    if n_apis <= 10 or loc <= 20: return "L4_advanced"
    return "L5_challenge"

def generate_html_report(results, output_path):
    s = results["summary"]; sp = results["success_patterns"]
    spv = results["success_vs_failure"]; curr = results["sft_curriculum"]
    html = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R89: DeepSeek \u6210\u529f\u8f68\u8ff9\u6a21\u5f0f\u6316\u6398 \u2014 SFT \u6b63\u4f8b\u8bfe\u7a0b\u8bbe\u8ba1</title>
<style>
body {{ font-family: -apple-system, "Segoe UI", Roboto, "Noto Sans SC", sans-serif; max-width: 1100px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #333; }}
h1 {{ color: #1a5276; border-bottom: 3px solid #2980b9; padding-bottom: 10px; }}
h2 {{ color: #2874a6; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 10px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; background: white; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #e8f4fd; color: #1a5276; font-weight: 600; }}
tr:nth-child(even) {{ background: #f8f9fa; }}
.good {{ color: #27ae60; font-weight: bold; }}
.bad {{ color: #c0392b; font-weight: bold; }}
.note {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px 15px; margin: 15px 0; }}
.key {{ background: #d4edda; border-left: 4px solid #28a745; padding: 10px 15px; margin: 15px 0; }}
code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }}
.tag {{ display: inline-block; background: #3498db; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 5px; }}
</style></head><body>
<h1>R89: DeepSeek \u6210\u529f\u8f68\u8ff9\u6a21\u5f0f\u6316\u6398 \u2014 SFT \u6b63\u4f8b\u8bfe\u7a0b\u8bbe\u8ba1\u4e0e API \u4f7f\u7528\u6a21\u5f0f\u5206\u6790</h1>
<p><span class="tag">wake137</span> <span class="tag">\u96f6GPU</span> <span class="tag">Python 3.8+ stdlib</span></p>
<h2>1. \u7814\u7a76\u76ee\u6807</h2>
<p>R88 \u5206\u6790\u4e86 20 \u4e2a\u5931\u8d25\u6848\u4f8b\uff1bR89 \u8865\u5168\u53e6\u4e00\u4fa7 \u2014 \u6316\u6398 <strong>83 \u4e2a\u6210\u529f\u8f68\u8ff9</strong>\u4e2d\u7684\u201c\u83b7\u80dc\u6a21\u5f0f\u201d\uff0c\u4e3a SFT \u6b63\u4f8b\u8bfe\u7a0b\u8bbe\u8ba1\u63d0\u4f9b\u5b9e\u8bc1\u4f9d\u636e\u3002</p>
<h2>2. \u6570\u636e\u6982\u51b5</h2>
<table><tr><th>\u6307\u6807</th><th>\u503c</th></tr>
<tr><td>\u603b\u8f68\u8ff9\u6570</td><td>{s['total_traces']}</td></tr>
<tr><td>\u6210\u529f\u8f68\u8ff9</td><td><span class="good">{s['success_count']}</span></td></tr>
<tr><td>\u5931\u8d25\u8f68\u8ff9</td><td><span class="bad">{s['failure_count']}</span></td></tr>
<tr><td>\u6210\u529f\u7387</td><td>{s['success_rate']:.1f}%</td></tr>
</table>
<h2>3. \u6210\u529f\u8f68\u8ff9\u5de5\u5177\u4f7f\u7528\u7edf\u8ba1</h2>
<table><tr><th>\u6307\u6807</th><th>\u5747\u503c</th><th>\u4e2d\u4f4d</th><th>\u6807\u51c6\u5dee</th><th>\u6700\u5c0f</th><th>\u6700\u5927</th></tr>
'''
    stats_rows = [
        ("\u5bf9\u8bdd\u957f\u5ea6", sp['conv_len_stats']),
        ("\u5de5\u5177\u8c03\u7528\u603b\u6570", sp['tool_calls_stats']),
        ("search_apis \u6b21\u6570", sp['search_apis_stats']),
        ("get_api_details \u6b21\u6570", sp['get_details_stats']),
        ("write_to_file \u6b21\u6570", sp['write_file_stats']),
        ("execute_command \u6b21\u6570", sp['exec_cmd_stats']),
        ("\u4ee3\u7801\u884c\u6570", sp['code_lines_stats']),
        ("\u4fee\u590d\u5faa\u73af\u6b21\u6570", sp['fix_cycles_stats']),
        ("\u552f\u4e00\u641c\u7d22 API \u6570", sp['unique_apis_stats']),
    ]
    for label, st in stats_rows:
        html += f"<tr><td>{label}</td><td>{st['mean']}</td><td>{st['median']}</td><td>{st['std']}</td><td>{st['min']}</td><td>{st['max']}</td></tr>\n"
    html += "</table>\n"
    html += '<h2>4. \u5de5\u5177\u8c03\u7528\u9891\u7387\u5206\u5e03</h2><table><tr><th>\u5de5\u5177</th><th>\u51fa\u73b0\u7387</th><th>\u5e73\u5747\u6b21\u6570</th></tr>\n'
    for tool, fd in sorted(sp["tool_frequency"].items(), key=lambda x: -x[1]["appearance_rate"]):
        html += f'<tr><td><code>{tool}</code></td><td>{fd["appearance_rate"]:.1f}%</td><td>{fd["avg_when_present"]:.1f}</td></tr>\n'
    html += '</table>\n'
    html += '<h2>5. \u5e38\u89c1\u5de5\u5177\u8c03\u7528\u5e8f\u5217 (n-gram)</h2><table><tr><th>\u5e8f\u5217</th><th>\u51fa\u73b0\u6b21\u6570</th><th>\u51fa\u73b0\u7387</th></tr>\n'
    arrow = " \u2192 "
    for item in sp["common_sequences"][:15]:
        seq = item["sequence"]
        count = item["count"]
        seq_str = arrow.join(seq)
        rate = count / s["success_count"] * 100 if s["success_count"] else 0
        html += f'<tr><td>{seq_str}</td><td>{count}</td><td>{rate:.1f}%</td></tr>\n'
    html += '</table>\n'
    html += '<h2>6. \u6210\u529f vs \u5931\u8d25\u5bf9\u6bd4</h2><table><tr><th>\u6307\u6807</th><th>\u6210\u529f(\u5747\u503c)</th><th>\u5931\u8d25(\u5747\u503c)</th><th>\u5dee\u5f02</th><th>\u5224\u8bfb</th></tr>\n'
    for metric, data in spv.items():
        diff = data["success_mean"] - data["failure_mean"]
        html += f'<tr><td>{data["label"]}</td><td>{data["success_mean"]:.1f}</td><td>{data["failure_mean"]:.1f}</td><td>{diff:+.1f}</td><td>{data.get("judgment","")}</td></tr>\n'
    html += '</table>\n'
    html += '<h2>7. \u6309\u573a\u666f\u5206\u6790</h2><table><tr><th>\u573a\u666f</th><th>\u6210\u529f</th><th>\u5931\u8d25</th><th>\u6210\u529f\u7387</th><th>\u5e73\u5747\u5de5\u5177\u8c03\u7528</th></tr>\n'
    for sc, data in sorted(sp["by_scenario"].items()):
        html += f'<tr><td>{sc}</td><td>{data["success"]}</td><td>{data["failure"]}</td><td>{data["success_rate"]:.1f}%</td><td>{data["avg_tool_calls"]:.1f}</td></tr>\n'
    html += '</table>\n'
    html += '<h2>8. \u6309\u96be\u5ea6\u5c42\u5206\u6790</h2><table><tr><th>\u96be\u5ea6</th><th>\u6210\u529f</th><th>\u5931\u8d25</th><th>\u6210\u529f\u7387</th><th>\u5e73\u5747\u5de5\u5177</th><th>\u5e73\u5747\u641c\u7d22</th></tr>\n'
    for dl, data in sorted(sp["by_difficulty"].items()):
        html += f'<tr><td>{dl}</td><td>{data["success"]}</td><td>{data["failure"]}</td><td>{data["success_rate"]:.1f}%</td><td>{data["avg_tool_calls"]:.1f}</td><td>{data["avg_search"]:.1f}</td></tr>\n'
    html += '</table>\n'
    html += f'<h2>9. SFT \u6b63\u4f8b\u8bfe\u7a0b\u8bbe\u8ba1\u5efa\u8bae</h2><div class="key"><p>{curr["coverage_gap"]}</p></div>'
    html += '<h3>9.1 \u4f18\u5148\u7ea7\u6392\u5e8f</h3><table><tr><th>\u4f18\u5148\u7ea7</th><th>\u7b5b\u9009\u6761\u4ef6</th><th>\u5019\u9009\u6570</th><th>\u7406\u7531</th></tr>\n'
    for p in curr["priority_tiers"]:
        html += f'<tr><td>{p["tier"]}</td><td>{p["criteria"]}</td><td>{p["count"]}</td><td>{p["rationale"]}</td></tr>\n'
    html += '</table>\n'
    html += '<h3>9.2 \u8bfe\u7a0b\u9636\u6bb5</h3><table><tr><th>\u9636\u6bb5</th><th>\u6570\u636e\u6765\u6e90</th><th>\u76ee\u6807</th><th>\u6837\u672c\u6570</th></tr>\n'
    for ph in curr["curriculum_phases"]:
        html += f'<tr><td>{ph["phase"]}</td><td>{ph["source"]}</td><td>{ph["goal"]}</td><td>{ph["samples"]}</td></tr>\n'
    html += '</table>\n'
    html += '<h2>10. API \u53d1\u73b0\u7b56\u7565\u5206\u6790</h2><div class="key"><p>search_apis \u4f7f\u7528\u7387: '
    html += f'{sp["search_usage_rate"]:.1f}%\uff0c\u96f6\u641c\u7d22\u6210\u529f\u7387: {sp["zero_search_rate"]:.1f}%\uff0cAPI \u53d1\u73b0\u95f4\u9694\u5747\u503c: {sp["api_discovery_gap_stats"]["mean"]}\u6761\u6d88\u606f</p></div>'
    html += '<h2>11. \u8bad\u7ec3\u7ba1\u7ebf\u5efa\u8bae</h2><table><tr><th>\u9636\u6bb5</th><th>\u5efa\u8bae</th><th>\u4f9d\u636e</th></tr>\n'
    for rec in curr["training_recommendations"]:
        html += f'<tr><td>{rec["stage"]}</td><td>{rec["recommendation"]}</td><td>{rec["evidence"]}</td></tr>\n'
    html += f'''</table>
<h2>12. \u5c40\u9650\u6027\u4e0e\u4e0b\u4e00\u6b65</h2>
<div class="note"><ul>
<li><strong>\u6837\u672c\u5c40\u9650</strong>: 83 \u4e2a\u6210\u529f\u8f68\u8ff9\u6765\u81ea DeepSeek(94%), MiniCPM5-2B(36%) \u7684\u6210\u529f\u6a21\u5f0f\u53ef\u80fd\u4e0d\u540c</li>
<li><strong>\u4e0b\u4e00\u6b65</strong>: GPU \u91ca\u653e\u540e\u7528 MiniCPM5-2B 36% \u4fa7\u771f\u5b9e\u8f68\u8ff9\u9a8c\u8bc1\u672c\u8282\u5047\u8bbe</li>
</ul></div>
<hr><p style="text-align:center;color:#999;font-size:0.85em;">R89 \u00b7 BaiZe Stage(ii) Post-Training \u00b7 {time.strftime('%Y-%m-%d %H:%M')} \u00b7 \u96f6 GPU \u00b7 \u7eaf Python 3.8+ stdlib</p>
</body></html>'''
    with open(output_path, "w", encoding="utf-8") as f: f.write(html)
    return len(html)

def main():
    print("=" * 70)
    print("R89: DeepSeek Success Trace Pattern Mining")
    print("     SFT Positive Curriculum Design & API Usage Pattern Analysis")
    print("=" * 70)
    print("\n[1/6] Loading dataset...")
    dataset = load_dataset()
    print(f"  Dataset: {len(dataset)} tasks")
    error_ids = extract_error_case_ids()
    print(f"  Error case IDs: {len(error_ids)}")
    print("\n[2/6] Loading all 103 traces...")
    traces = load_all_traces(dataset, error_ids)
    print(f"  Loaded: {len(traces)} traces")
    success_traces = [t for t in traces if not t["is_error"]]
    failure_traces = [t for t in traces if t["is_error"]]
    print(f"  Success: {len(success_traces)}, Failure: {len(failure_traces)}")
    print("\n[3/6] Analyzing trace patterns...")
    all_analyses = []
    for t in traces:
        a = analyze_trace(t)
        a["is_error"] = t["is_error"]; a["task_id"] = t["task_id"]
        a["entry_point"] = t["entry_point"]; a["task_meta"] = t["task_meta"]
        a["difficulty"] = categorize_difficulty(t["task_meta"])
        a["scenario"] = t["task_meta"]["scenario"] if t["task_meta"] else "Unknown"
        all_analyses.append(a)
    success_analyses = [a for a in all_analyses if not a["is_error"]]
    failure_analyses = [a for a in all_analyses if a["is_error"]]
    print("\n[4/6] Computing success patterns...")
    def safe_stats(lst, key): return compute_statistics([a[key] for a in lst if key in a])
    conv_len_stats = safe_stats(success_analyses, "conv_len")
    tool_calls_stats = safe_stats(success_analyses, "tool_calls_total")
    search_apis_stats = safe_stats(success_analyses, "search_apis_count")
    get_details_stats = safe_stats(success_analyses, "get_api_details_count")
    write_file_stats = safe_stats(success_analyses, "write_to_file_count")
    exec_cmd_stats = safe_stats(success_analyses, "execute_command_count")
    code_lines_stats = safe_stats(success_analyses, "total_code_lines")
    fix_cycles_stats = safe_stats(success_analyses, "fix_cycles")
    unique_apis_stats = safe_stats(success_analyses, "unique_searched_apis")
    tool_freq_summary = {}
    all_tools = set()
    for a in success_analyses: all_tools.update(a.get("tool_freq", {}).keys())
    for tool in all_tools:
        appearances = [a.get("tool_freq", {}).get(tool, 0) for a in success_analyses]
        present = [v for v in appearances if v > 0]
        tool_freq_summary[tool] = {"appearance_rate": len(present)/len(success_analyses)*100 if success_analyses else 0, "avg_when_present": sum(present)/len(present) if present else 0}
    print("  Extracting common tool call sequences...")
    common_sequences = extract_common_sequences(success_analyses, 3, 6)
    top_sequences = common_sequences.most_common(15)
    gaps = [a["api_discovery_gap"] for a in success_analyses if a["api_discovery_gap"] is not None]
    api_discovery_gap_stats = compute_statistics(gaps)
    search_usage = sum(1 for a in success_analyses if a["search_apis_count"] > 0)
    search_usage_rate = search_usage / len(success_analyses) * 100 if success_analyses else 0
    zero_search_rate = 100 - search_usage_rate
    by_scenario = {}
    for a in all_analyses:
        sc = a["scenario"]
        if sc not in by_scenario: by_scenario[sc] = {"success": 0, "failure": 0, "tool_calls": [], "fix_cycles": []}
        if a["is_error"]: by_scenario[sc]["failure"] += 1
        else: by_scenario[sc]["success"] += 1; by_scenario[sc]["tool_calls"].append(a["tool_calls_total"]); by_scenario[sc]["fix_cycles"].append(a["fix_cycles"])
    for sc, data in by_scenario.items():
        total = data["success"] + data["failure"]
        data["success_rate"] = data["success"]/total*100 if total > 0 else 0
        data["avg_tool_calls"] = sum(data["tool_calls"])/len(data["tool_calls"]) if data["tool_calls"] else 0
        data["avg_fix_cycles"] = sum(data["fix_cycles"])/len(data["fix_cycles"]) if data["fix_cycles"] else 0
    by_difficulty = {}
    for a in all_analyses:
        dl = a["difficulty"]
        if dl not in by_difficulty: by_difficulty[dl] = {"success": 0, "failure": 0, "tool_calls": [], "search": [], "fix_cycles": []}
        if a["is_error"]: by_difficulty[dl]["failure"] += 1
        else: by_difficulty[dl]["success"] += 1; by_difficulty[dl]["tool_calls"].append(a["tool_calls_total"]); by_difficulty[dl]["search"].append(a["search_apis_count"]); by_difficulty[dl]["fix_cycles"].append(a["fix_cycles"])
    for dl, data in by_difficulty.items():
        total = data["success"] + data["failure"]
        data["success_rate"] = data["success"]/total*100 if total > 0 else 0
        data["avg_tool_calls"] = sum(data["tool_calls"])/len(data["tool_calls"]) if data["tool_calls"] else 0
        data["avg_search"] = sum(data["search"])/len(data["search"]) if data["search"] else 0
        data["avg_fix_cycles"] = sum(data["fix_cycles"])/len(data["fix_cycles"]) if data["fix_cycles"] else 0
    print("\n[5/6] Computing success vs failure contrast...")
    def mean_for(lst, key):
        vals = [a.get(key, 0) for a in lst]; return sum(vals)/len(vals) if vals else 0
    success_vs_failure = {
        "conv_len": {"label": "\u5bf9\u8bdd\u957f\u5ea6", "success_mean": mean_for(success_analyses, "conv_len"), "failure_mean": mean_for(failure_analyses, "conv_len"), "judgment": "\u6210\u529f\u66f4\u957f" if mean_for(success_analyses, "conv_len") > mean_for(failure_analyses, "conv_len") else "\u5931\u8d25\u66f4\u957f"},
        "tool_calls": {"label": "\u5de5\u5177\u8c03\u7528\u603b\u6570", "success_mean": mean_for(success_analyses, "tool_calls_total"), "failure_mean": mean_for(failure_analyses, "tool_calls_total"), "judgment": "\u6210\u529f\u66f4\u591a" if mean_for(success_analyses, "tool_calls_total") > mean_for(failure_analyses, "tool_calls_total") else "\u5931\u8d25\u66f4\u591a"},
        "search_apis": {"label": "search_apis \u6b21\u6570", "success_mean": mean_for(success_analyses, "search_apis_count"), "failure_mean": mean_for(failure_analyses, "search_apis_count"), "judgment": "\u6210\u529f\u641c\u7d22\u66f4\u591a" if mean_for(success_analyses, "search_apis_count") > mean_for(failure_analyses, "search_apis_count") else "\u5931\u8d25\u641c\u7d22\u66f4\u591a"},
        "get_details": {"label": "get_api_details \u6b21\u6570", "success_mean": mean_for(success_analyses, "get_api_details_count"), "failure_mean": mean_for(failure_analyses, "get_api_details_count"), "judgment": "\u6210\u529f\u67e5\u770b\u66f4\u591a" if mean_for(success_analyses, "get_api_details_count") > mean_for(failure_analyses, "get_api_details_count") else "\u5931\u8d25\u67e5\u770b\u66f4\u591a"},
        "write_file": {"label": "write_to_file \u6b21\u6570", "success_mean": mean_for(success_analyses, "write_to_file_count"), "failure_mean": mean_for(failure_analyses, "write_to_file_count"), "judgment": "\u6210\u529f\u5199\u66f4\u591a" if mean_for(success_analyses, "write_to_file_count") > mean_for(failure_analyses, "write_to_file_count") else "\u5931\u8d25\u5199\u66f4\u591a"},
        "exec_cmd": {"label": "execute_command \u6b21\u6570", "success_mean": mean_for(success_analyses, "execute_command_count"), "failure_mean": mean_for(failure_analyses, "execute_command_count"), "judgment": "\u6210\u529f\u6267\u884c\u66f4\u591a" if mean_for(success_analyses, "execute_command_count") > mean_for(failure_analyses, "execute_command_count") else "\u5931\u8d25\u6267\u884c\u66f4\u591a"},
        "fix_cycles": {"label": "\u4fee\u590d\u5faa\u73af\u6b21\u6570", "success_mean": mean_for(success_analyses, "fix_cycles"), "failure_mean": mean_for(failure_analyses, "fix_cycles"), "judgment": "\u6210\u529f\u4fee\u590d\u66f4\u591a" if mean_for(success_analyses, "fix_cycles") > mean_for(failure_analyses, "fix_cycles") else "\u5931\u8d25\u4fee\u590d\u66f4\u591a"},
        "code_lines": {"label": "\u4ee3\u7801\u884c\u6570", "success_mean": mean_for(success_analyses, "total_code_lines"), "failure_mean": mean_for(failure_analyses, "total_code_lines"), "judgment": "\u6210\u529f\u5199\u66f4\u591a" if mean_for(success_analyses, "total_code_lines") > mean_for(failure_analyses, "total_code_lines") else "\u5931\u8d25\u5199\u66f4\u591a"},
        "unique_apis": {"label": "\u552f\u4e00\u641c\u7d22 API \u6570", "success_mean": mean_for(success_analyses, "unique_searched_apis"), "failure_mean": mean_for(failure_analyses, "unique_searched_apis"), "judgment": "\u6210\u529f\u63a2\u7d22\u66f4\u591a" if mean_for(success_analyses, "unique_searched_apis") > mean_for(failure_analyses, "unique_searched_apis") else "\u5931\u8d25\u63a2\u7d22\u66f4\u591a"},
    }
    print("  Designing SFT positive curriculum...")
    has_error_success = [a for a in success_analyses if a["has_errors"]]
    has_error_success_rate = len(has_error_success) / len(success_analyses) * 100 if success_analyses else 0
    tier1 = [a for a in success_analyses if not a["has_errors"] and a["tool_calls_total"] <= 15]
    tier2 = [a for a in success_analyses if a["has_errors"] and a["fix_cycles"] <= 3]
    tier3 = [a for a in success_analyses if a["fix_cycles"] > 3]
    tier4 = [a for a in success_analyses if a["search_apis_count"] >= 3]
    coverage_gap = (f"\u6210\u529f\u8f68\u8ff9\u4e2d {has_error_success_rate:.1f}% \u5305\u542b\u9519\u8bef\u4fee\u590d\u5faa\u73af\u3002"
        f"Tier1(\u5e72\u51c0\u8f68\u8ff9)={len(tier1)}, Tier2(\u6709\u9519\u4fee\u590d<=3)={len(tier2)}, "
        f"Tier3(\u591a\u6b21\u4fee\u590d)={len(tier3)}, Tier4(\u6df1\u5ea6API\u641c\u7d22)={len(tier4)}\u3002"
        f" SFT v2 \u8bed\u6599 19524 \u5bf9\u5e94\u786e\u4fdd\u8986\u76d6\u201c\u641c\u7d22->\u67e5->\u5199->\u6267\u884c->\u4fee\u590d\u201d\u5168\u95ed\u73af\u6a21\u5f0f\u3002")
    training_recommendations = [
        {"stage": "\u9886\u57df\u9000\u706b", "recommendation": "\u6ce8\u5165 API \u53d1\u73b0\u6a21\u5f0f: search_apis->get_api_details \u5e8f\u5217\u4f5c\u4e3a API \u6587\u6863\u68c0\u7d22\u8303\u4f8b", "evidence": f"search_apis \u4f7f\u7528\u7387 {search_usage_rate:.1f}%"},
        {"stage": "SFT", "recommendation": "\u6b63\u4f8b\u8bfe\u7a0b: Tier1->Tier2->Tier3 \u6e10\u8fdb\u5f0f\u589e\u52a0\u96be\u5ea6", "evidence": f"Tier1={len(tier1)}, Tier2={len(tier2)}, Tier3={len(tier3)}"},
        {"stage": "SFT", "recommendation": "\u786e\u4fdd SFT \u6570\u636e\u5305\u542b\u201c\u72af\u9519->\u4fee\u590d\u201d\u8fed\u4ee3\u8f68\u8ff9", "evidence": f"{has_error_success_rate:.1f}% \u6210\u529f\u8f68\u8ff9\u542b\u9519\u8bef\u4fee\u590d\u5faa\u73af"},
        {"stage": "RL(GRPO)", "recommendation": "RL \u8bfe\u7a0b\u4ece L3 \u5f00\u59cb(\u4e0e R88 \u4e00\u81f4), \u91cd\u70b9\u8bad\u7ec3\u95ed\u73af", "evidence": f"L3 \u6210\u529f\u7387 {by_difficulty.get('L3_medium',{}).get('success_rate',0):.1f}%"},
        {"stage": "RL(GRPO)", "recommendation": "techlib \u4f9d\u8d56\u4efb\u52a1\u964d\u4f4e RL \u6743\u91cd(\u4e0e R88 \u4e00\u81f4)", "evidence": "\u5931\u8d25\u4e3b\u8981\u4e3a\u73af\u5883\u9650\u5236\u975e\u7b56\u7565\u95ee\u9898"},
    ]
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {"total_traces": len(traces), "success_count": len(success_traces), "failure_count": len(failure_traces), "success_rate": len(success_traces)/len(traces)*100 if traces else 0, "matched_tasks": sum(1 for t in traces if t["task_id"])},
        "success_patterns": {"conv_len_stats": conv_len_stats, "tool_calls_stats": tool_calls_stats, "search_apis_stats": search_apis_stats, "get_details_stats": get_details_stats, "write_file_stats": write_file_stats, "exec_cmd_stats": exec_cmd_stats, "code_lines_stats": code_lines_stats, "fix_cycles_stats": fix_cycles_stats, "unique_apis_stats": unique_apis_stats, "tool_frequency": tool_freq_summary, "common_sequences": [{"sequence": list(s), "count": c} for s, c in top_sequences], "api_discovery_gap_stats": api_discovery_gap_stats, "search_usage_rate": search_usage_rate, "zero_search_rate": zero_search_rate, "by_scenario": by_scenario, "by_difficulty": by_difficulty},
        "success_vs_failure": success_vs_failure,
        "sft_curriculum": {"has_error_success_rate": has_error_success_rate, "priority_tiers": [{"tier": "Tier1", "criteria": "\u65e0\u9519\u8bef+<=15\u5de5\u5177\u8c03\u7528", "count": len(tier1), "rationale": "\u5e72\u51c0\u77ed\u8f68\u8ff9, SFT \u521d\u671f"}, {"tier": "Tier2", "criteria": "\u6709\u9519\u4f46\u4fee\u590d<=3\u6b21", "count": len(tier2), "rationale": "\u5c55\u793a\u72af\u9519->\u4fee\u590d\u95ed\u73af"}, {"tier": "Tier3", "criteria": "\u4fee\u590d>3\u6b21", "count": len(tier3), "rationale": "\u590d\u6742\u4efb\u52a1\u8fed\u4ee3, SFT \u540e\u671f"}, {"tier": "Tier4", "criteria": "search_apis>=3\u6b21", "count": len(tier4), "rationale": "API \u53d1\u73b0\u7b56\u7565\u8303\u4f8b"}], "curriculum_phases": [{"phase": "Phase1", "source": "Tier1", "goal": "\u5efa\u7acb\u57fa\u672c\u95ed\u73af", "samples": len(tier1)}, {"phase": "Phase2", "source": "Tier2", "goal": "\u5b66\u4e60\u72af\u9519->\u4fee\u590d", "samples": len(tier2)}, {"phase": "Phase3", "source": "Tier3+Tier4", "goal": "\u590d\u6742\u95ee\u9898+API\u6df1\u5ea6\u63a2\u7d22", "samples": len(tier3)+len(tier4)}], "coverage_gap": coverage_gap, "training_recommendations": training_recommendations},
    }
    json_path = os.path.join(RUN_DIR, "r89_results.json")
    with open(json_path, "w", encoding="utf-8") as f: json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  JSON saved: {json_path} ({os.path.getsize(json_path)//1024}KB)")
    print("\n[6/6] Generating HTML report...")
    html_path = os.path.join(REPORT_DIR, "report_posttrain_r89_ds_success_patterns_zh.html")
    html_size = generate_html_report(results, html_path)
    print(f"  HTML saved: {html_path} ({html_size//1024}KB)")
    print("\n" + "=" * 70)
    print("KEY FINDINGS:")
    print("=" * 70)
    print(f"  Success traces: {len(success_traces)}/{len(traces)} ({results['summary']['success_rate']:.1f}%)")
    print(f"  Avg tool calls (success): {tool_calls_stats['mean']:.1f}")
    print(f"  Avg fix cycles (success): {fix_cycles_stats['mean']:.1f}")
    print(f"  Has-error-but-succeeded: {has_error_success_rate:.1f}%")
    print(f"  Search API usage rate: {search_usage_rate:.1f}%")
    print(f"  Top sequence: {' -> '.join(top_sequences[0][0]) if top_sequences else 'N/A'} ({top_sequences[0][1] if top_sequences else 0}x)")
    print(f"  Tier1={len(tier1)}, Tier2={len(tier2)}, Tier3={len(tier3)}, Tier4={len(tier4)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
