#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""trace_anatomy.py —— Cline session JSONL 轨迹解剖器（trace anatomy）

用途：对本地归档的 Cline 轨迹目录做可复现的**行为学**指标统计，供论文 §5 使用。
仅依赖 Python 标准库（python3.8+，实测 python3.10），可在 Linux 集群直接运行；
**不依赖 pandas / numpy**。

用法：
    python trace_anatomy.py --glob "<pattern>" --out metrics.json [--md report.md]
    python trace_anatomy.py --selftest

--glob 的匹配结果可以是：
  * cline_session.jsonl 文件路径（glob）
  * case 目录路径（自动拼接 cline_session.jsonl）

目录约定（单个 case）：
    <case_id>/cline_session.jsonl   事件流（0.2MB~10MB）
    <case_id>/cline_stderr.log      Cline 侧 stderr
    <case_id>/outputs/              交付物目录
    <case_id>/assets/               输入素材目录

--------------------------------------------------------------------------
实测确认的 session JSONL 结构（本脚本据此解析，2026-11 实测 48 份轨迹）
--------------------------------------------------------------------------
每行一个 JSON 对象。顶层 type 共 4 种：
  1) "hook_event"   键: ts, type, hookEventName, agentId, taskId, parentAgentId
                    hookEventName ∈ {agent_start, tool_call, tool_result, agent_end, agent_error}
                    ← 注意：tool_call / tool_result **只带时间戳，没有工具名与内容**，
                      因此任何 toolName 统计必须走 agent_event.content_start(tool)。
  2) "agent_event"  键: ts, type, event{...}
                    event.type ∈ {
                        iteration_start : iteration
                        content_start   : contentType ∈ {reasoning, text, tool}
                                          reasoning → reasoning(增量文本), redacted
                                          text      → text(增量文本), accumulated(累计文本)
                                          tool      → toolName, toolCallId, input(dict)
                        content_end     : contentType ∈ {reasoning, text, tool}
                                          tool → toolName, toolCallId, output, durationMs[, error]
                        usage           : inputTokens, outputTokens, totalInputTokens,
                                          totalOutputTokens, totalCost   ← 每次 API 调用的用量
                        iteration_end   : iteration, hadToolCalls, toolCallCount
                        notice          : noticeType, displayRole, message, reason, metadata
                                          （metadata.kind == "auto_compaction" 表示上下文自动压缩）
                        error           : error{name,message,stack}, recoverable, iteration
                        done            : reason, iterations, usage{inputTokens,outputTokens,totalCost}, text
                    }
  3) "run_result"   键: ts, type, finishReason, iterations, usage{inputTokens,outputTokens,
                    cacheReadTokens,cacheWriteTokens,totalCost}, aggregateUsage{同 usage},
                    durationMs, model{id,provider}, text
                    ← **这是唯一带 cache 字段与 aggregateUsage 的权威总量记录**，
                      只有部分 trace 有（本批 30/48）。
  4) "run_aborted"  键: ts, type, reason, message

结论（写进报告的 usage 字段说明）：
  * 单次调用的 usage 事件字段 = inputTokens / outputTokens / totalInputTokens /
    totalOutputTokens / totalCost，**没有 cacheReadTokens / cacheWriteTokens**；
  * 权威总量取 run_result.aggregateUsage = inputTokens / outputTokens /
    cacheReadTokens / cacheWriteTokens / totalCost；
  * usage 事件的 inputTokens 是**每次请求**的输入 token，直接求和会重复计入上下文，
    不能当作总成本，故本脚本把两者分开记录（tokens / tokens_usage_event_sum）。
"""

import argparse
import glob
import json
import os
import re
import statistics
import sys
import time
from datetime import datetime

VERSION = "1.0.0"

# ---------------------------------------------------------------- 错误信号定义
# error_signals 的统计口径（写死在代码里，报告照抄）：
#   对两处文本分别做 **不区分大小写** 的正则 findall 计数（非重叠匹配）：
#     A) cline_stderr.log 全文           → 键 "stderr"
#     B) trace 的最终文本语料            → 键 "text"
#        （优先 run_result.text，其次 done.text，其次最后一条 text.accumulated）
#   每条正则的匹配数相加得 "total"；error_signal_total = 所有 pattern 的 total 之和。
ERROR_PATTERNS = [
    ("error", r"error"),
    ("traceback", r"traceback"),
    ("timeout", r"timeout"),
    ("mcp", r"mcp"),
    ("exception", r"exception"),
    ("failed", r"failed"),
    ("permission_denied", r"permission denied"),
]

# .zip 相关：submit.zip 视为“提交动作”，任意 *.zip 视为“打包/压缩动作”
RE_SUBMIT_ZIP = re.compile(r"submit\.zip", re.IGNORECASE)
RE_ANY_ZIP = re.compile(r"[^\s\"'`,;)]*\.zip\b", re.IGNORECASE)

TS_FORMATS = ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ")


def parse_ts(s):
    """解析 ISO8601 UTC 时间串，失败返回 None。"""
    if not isinstance(s, str):
        return None
    for fmt in TS_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------- 小工具
def percentile(values, p):
    """线性插值分位数（与 numpy 默认 'linear' 口径一致），空列表返回 None。"""
    vs = sorted(v for v in values if v is not None)
    if not vs:
        return None
    if len(vs) == 1:
        return float(vs[0])
    rank = (len(vs) - 1) * (p / 100.0)
    lo = int(rank)
    hi = min(lo + 1, len(vs) - 1)
    frac = rank - lo
    return float(vs[lo]) + (vs[hi] - vs[lo]) * frac


def dist(values):
    """分布统计：n / median / p25 / p75 / mean / min / max。"""
    vs = sorted(v for v in values if v is not None)
    if not vs:
        return {"n": 0, "median": None, "p25": None, "p75": None,
                "mean": None, "min": None, "max": None}
    return {
        "n": len(vs),
        "median": float(statistics.median(vs)),
        "p25": percentile(vs, 25),
        "p75": percentile(vs, 75),
        "mean": float(sum(vs)) / len(vs),
        "min": float(vs[0]),
        "max": float(vs[-1]),
    }


def count_patterns(text):
    """按 ERROR_PATTERNS 统计匹配次数（不区分大小写、非重叠）。"""
    out = {}
    for name, pat in ERROR_PATTERNS:
        out[name] = len(re.findall(pat, text, re.IGNORECASE)) if text else 0
    return out


def scan_dir(path):
    """递归统计目录下文件：返回 (文件数, 非空文件数, 总字节)。目录不存在返回 (0,0,0)。"""
    n = n_nonempty = total = 0
    if not os.path.isdir(path):
        return 0, 0, 0
    for root, _dirs, files in os.walk(path):
        for fn in files:
            fp = os.path.join(root, fn)
            try:
                size = os.path.getsize(fp)
            except OSError:
                continue
            n += 1
            total += size
            if size > 0:
                n_nonempty += 1
    return n, n_nonempty, total


def list_output_names(path, limit=40):
    """列出 outputs/ 下的非空文件（相对路径，正斜杠），用于人工抽查。"""
    names = []
    if not os.path.isdir(path):
        return names
    for root, _dirs, files in os.walk(path):
        for fn in files:
            fp = os.path.join(root, fn)
            try:
                if os.path.getsize(fp) > 0:
                    names.append(os.path.relpath(fp, path).replace("\\", "/"))
            except OSError:
                pass
    names.sort()
    return names[:limit]


def read_text(path, limit_bytes=None):
    """读文本文件（UTF-8, 坏字节替换），可选截断；不存在返回 ''。"""
    if not os.path.isfile(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            return f.read() if limit_bytes is None else f.read(limit_bytes)
    except OSError:
        return ""

def analyze_case(session_path, case_dir=None):
    """解剖单个 trace。session 缺失/为空时仍返回目录侧指标，行为指标置零。"""
    session_path = os.path.abspath(session_path)
    if case_dir is None:
        case_dir = os.path.dirname(session_path)
    case_id = os.path.basename(os.path.normpath(case_dir))

    rec = {
        "case_id": case_id,
        "session_path": session_path,
        "session_present": os.path.isfile(session_path),
        "session_bytes": os.path.getsize(session_path) if os.path.isfile(session_path) else 0,
        "session_lines": 0,
        "session_bad_lines": 0,
        "ts_first": None, "ts_last": None,
        "wall_seconds": None,
        "duration_ms_from_run_result": None,
        "n_iterations": 0,
        "n_iterations_run_result": None,
        "n_tool_calls": 0,
        "n_tool_calls_hook_xcheck": 0,
        "tool_histogram": {},
        "n_reasoning_chunks": 0,
        "n_text_chunks": 0,
        "reasoning_chars": 0,
        "text_chars_final": 0,
        "final_text_source": None,
        "tokens": None,
        "tokens_source": None,
        "tokens_usage_event_sum": None,
        "n_usage_events": 0,
        "submit_attempts": 0,
        "zip_mention_tool_calls": 0,
        "n_output_files": 0,
        "n_output_files_nonempty": 0,
        "output_bytes": 0,
        "has_zip_in_outputs": False,
        "n_asset_files": 0,
        "asset_bytes": 0,
        "ended_with_tag": None,
        "ending_detail": None,
        "finish_reason": None,
        "last_event_type": None,
        "model": None,
        "n_error_events": 0,
        "n_notices": 0,
        "n_auto_compactions": 0,
        "n_done_events": 0,
        "n_tool_content_end_errors": 0,
        "n_declare_done_tool_calls": 0,
        "error_signals": {},
        "error_signal_total": 0,
        "stderr_bytes": 0,
        "produced_output": False,
    }

    outputs_dir = os.path.join(case_dir, "outputs")
    assets_dir = os.path.join(case_dir, "assets")
    stderr_path = os.path.join(case_dir, "cline_stderr.log")

    # ---------------- 目录侧指标
    n_all, n_nonempty, obytes = scan_dir(outputs_dir)
    rec["n_output_files"] = n_all
    rec["n_output_files_nonempty"] = n_nonempty
    rec["output_bytes"] = obytes
    out_names = list_output_names(outputs_dir, limit=300)
    rec["has_zip_in_outputs"] = any(x.lower().endswith(".zip") for x in out_names)
    na, _na_ne, abytes = scan_dir(assets_dir)
    rec["n_asset_files"] = na
    rec["asset_bytes"] = abytes
    # produced_output 定义：outputs/ 下至少存在 1 个字节数 > 0 的文件。
    # 注意这只代表“产物存在”，不代表正确性（本地无 judge verdict）。
    rec["produced_output"] = n_nonempty > 0

    stderr_text = read_text(stderr_path)
    rec["stderr_bytes"] = os.path.getsize(stderr_path) if os.path.isfile(stderr_path) else 0

    if not rec["session_present"] or rec["session_bytes"] == 0:
        rec["ended_with_tag"] = "empty_session" if rec["session_present"] else "no_session"
        rec["ending_detail"] = ("cline_session.jsonl 为 0 字节" if rec["session_present"]
                                else "无 cline_session.jsonl")
        sig = count_patterns(stderr_text)
        zero = {k: 0 for k, _ in ERROR_PATTERNS}
        rec["error_signals"] = {"stderr": sig, "text": zero, "total": dict(sig)}
        rec["error_signal_total"] = sum(sig.values())
        return rec


    # ---------------- 主循环
    tool_hist = {}
    n_tool = n_reason = n_text = 0
    reason_chars = 0
    n_iter_start = 0
    n_tool_hook = 0
    n_usage = 0
    sum_in = sum_out = 0
    sum_cost = 0.0
    submit = zipm = 0
    n_err_ev = n_notice = n_compact = n_done = n_tool_ce_err = n_declare_done = 0
    run_result = None
    run_aborted = None
    done_text = None
    last_event_type = None
    last_text_accum = None
    last_error_msg = None
    first_ts = last_ts = None
    lines = 0
    bad = 0

    with open(session_path, "r", encoding="utf-8-sig", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            lines += 1
            try:
                obj = json.loads(line)
            except ValueError:
                bad += 1
                continue

            ts = parse_ts(obj.get("ts"))
            if ts is not None:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts

            ttype = obj.get("type")
            last_event_type = ttype

            if ttype == "hook_event":
                if obj.get("hookEventName") == "tool_call":
                    n_tool_hook += 1
                continue
            if ttype == "run_aborted":
                run_aborted = obj
                continue
            if ttype == "run_result":
                run_result = obj
                continue
            if ttype != "agent_event":
                continue

            ev = obj.get("event") or {}
            etype = ev.get("type")

            if etype == "iteration_start":
                n_iter_start += 1
            elif etype == "usage":
                n_usage += 1
                sum_in += int(ev.get("inputTokens") or 0)
                sum_out += int(ev.get("outputTokens") or 0)
                sum_cost += float(ev.get("totalCost") or 0)
            elif etype == "content_start":
                ct = ev.get("contentType")
                if ct == "reasoning":
                    n_reason += 1
                    reason_chars += len(ev.get("reasoning") or "")
                elif ct == "text":
                    n_text += 1
                    if isinstance(ev.get("accumulated"), str):
                        last_text_accum = ev["accumulated"]
                elif ct == "tool":
                    n_tool += 1
                    tname = ev.get("toolName") or "?"
                    tool_hist[tname] = tool_hist.get(tname, 0) + 1
                    if tname.split("__")[-1] == "declare_done":
                        n_declare_done += 1
                    blob = json.dumps(ev.get("input"), ensure_ascii=False, sort_keys=True)
                    if RE_SUBMIT_ZIP.search(blob):
                        submit += 1
                    if RE_ANY_ZIP.search(blob):
                        zipm += 1
            elif etype == "content_end":
                if ev.get("contentType") == "tool" and ev.get("error"):
                    n_tool_ce_err += 1
            elif etype == "notice":
                n_notice += 1
                md = ev.get("metadata") or {}
                if md.get("kind") == "auto_compaction" or ev.get("reason") == "auto_compaction":
                    n_compact += 1
            elif etype == "error":
                n_err_ev += 1
                err = ev.get("error") or {}
                last_error_msg = err.get("message") if isinstance(err, dict) else str(err)
            elif etype == "done":
                n_done += 1
                if isinstance(ev.get("text"), str):
                    done_text = ev["text"]

    rec["session_lines"] = lines
    rec["session_bad_lines"] = bad
    rec["n_iterations"] = n_iter_start
    rec["n_tool_calls"] = n_tool
    rec["n_tool_calls_hook_xcheck"] = n_tool_hook
    rec["tool_histogram"] = dict(sorted(tool_hist.items(), key=lambda kv: (-kv[1], kv[0])))
    rec["n_reasoning_chunks"] = n_reason
    rec["n_text_chunks"] = n_text
    rec["reasoning_chars"] = reason_chars
    rec["submit_attempts"] = submit
    rec["zip_mention_tool_calls"] = zipm
    rec["n_usage_events"] = n_usage
    rec["n_error_events"] = n_err_ev
    rec["n_notices"] = n_notice
    rec["n_auto_compactions"] = n_compact
    rec["n_done_events"] = n_done
    rec["n_tool_content_end_errors"] = n_tool_ce_err
    rec["n_declare_done_tool_calls"] = n_declare_done
    rec["last_event_type"] = last_event_type

    if first_ts is not None and last_ts is not None:
        rec["ts_first"] = first_ts.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (first_ts.microsecond // 1000)
        rec["ts_last"] = last_ts.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (last_ts.microsecond // 1000)
        rec["wall_seconds"] = round((last_ts - first_ts).total_seconds(), 3)

    # ---------------- tokens：优先 run_result.aggregateUsage（权威总量）
    if run_result is not None:
        au = run_result.get("aggregateUsage") or run_result.get("usage") or {}
        rec["tokens"] = {
            "input": au.get("inputTokens"),
            "output": au.get("outputTokens"),
            "cache_read": au.get("cacheReadTokens"),
            "cache_write": au.get("cacheWriteTokens"),
            "cost": au.get("totalCost"),
        }
        rec["tokens_source"] = "run_result.aggregateUsage"
        rec["n_iterations_run_result"] = run_result.get("iterations")
        rec["finish_reason"] = run_result.get("finishReason")
        rec["duration_ms_from_run_result"] = run_result.get("durationMs")
        m = run_result.get("model")
        if isinstance(m, dict):
            rec["model"] = m.get("id")
        elif isinstance(m, str):
            rec["model"] = m
    elif n_usage > 0:
        rec["tokens"] = {"input": sum_in, "output": sum_out,
                         "cache_read": None, "cache_write": None, "cost": sum_cost}
        rec["tokens_source"] = "sum(usage events) PER_REQUEST_SUM_NOT_TOTAL"
        rec["tokens_usage_event_sum"] = {"input": sum_in, "output": sum_out, "cost": sum_cost}

    # ---------------- 最终文本语料（只取一份，避免增量文本重复计数）
    if run_result is not None and isinstance(run_result.get("text"), str):
        final_text, src = run_result["text"], "run_result.text"
    elif done_text is not None:
        final_text, src = done_text, "done.text"
    elif last_text_accum is not None:
        final_text, src = last_text_accum, "last_text.accumulated"
    else:
        final_text, src = "", "none"
    rec["text_chars_final"] = len(final_text)
    rec["final_text_source"] = src

    # ---------------- 终止形态（ended_with_tag）
    if run_aborted is not None:
        rec["ended_with_tag"] = "aborted"
        rec["finish_reason"] = "aborted"
        rec["ending_detail"] = "%s | %s" % (run_aborted.get("reason"), run_aborted.get("message"))
    elif run_result is not None:
        fr = (run_result.get("finishReason") or "")
        low = fr.lower()
        rec["ended_with_tag"] = "completed" if low == "completed" else (low or "completed_no_reason")
        if low == "aborted":
            rec["ended_with_tag"] = "aborted"
        rec["ending_detail"] = "finishReason=%s | 末文本 %d 字符" % (fr, len(final_text.strip()))
    elif n_err_ev > 0 and n_done == 0:
        rec["ended_with_tag"] = "error"
        rec["ending_detail"] = "无 run_result | 末条 error: %s" % (str(last_error_msg)[:200],)
    elif n_done > 0:
        rec["ended_with_tag"] = "done_event_only"
        rec["ending_detail"] = "有 done 事件但无 run_result | 末文本 %d 字符" % len(final_text.strip())
    else:
        rec["ended_with_tag"] = "no_terminator"
        rec["ending_detail"] = "无 run_result/run_aborted/done/error（采集被截断）"

    # ---------------- 错误信号
    sig_err = count_patterns(stderr_text)
    sig_txt = count_patterns(final_text)
    rec["error_signals"] = {
        "stderr": sig_err,
        "text": sig_txt,
        "total": {k: sig_err[k] + sig_txt[k] for k, _ in ERROR_PATTERNS},
    }
    rec["error_signal_total"] = sum(rec["error_signals"]["total"].values())
    return rec



# ---------------------------------------------------------------- 聚合
def is_mcp_tool(name):
    """MCP 类工具判定：按 Cline 的 `server__tool` 命名约定，名字含 '__' 即视为 MCP server 工具。
    本批数据里实际出现的 MCP 前缀是 `eda_flow__` 与 `pyAether_MCP_server__`，
    字面 `mcp__` 前缀出现 0 次（见报告）。"""
    return "__" in name


def aggregate(records, runtime_seconds=None, glob_pattern=None):
    cases = sorted(records, key=lambda r: r["case_id"])
    with_session = [r for r in cases if r["session_present"] and r["session_bytes"] > 0]
    ts_all = [r["ts_first"] for r in cases if r["ts_first"]]
    ts_all_end = [r["ts_last"] for r in cases if r["ts_last"]]

    tool_counts = {}
    tool_trace_counts = {}
    for r in cases:
        for name, c in r["tool_histogram"].items():
            tool_counts[name] = tool_counts.get(name, 0) + c
            tool_trace_counts[name] = tool_trace_counts.get(name, 0) + 1

    mcp_calls = sum(c for n, c in tool_counts.items() if is_mcp_tool(n))
    non_mcp_calls = sum(c for n, c in tool_counts.items() if not is_mcp_tool(n))
    total_calls = mcp_calls + non_mcp_calls

    tool_table = [
        {
            "tool": n,
            "calls": c,
            "traces": tool_trace_counts[n],
            "is_mcp": is_mcp_tool(n),
            "call_share": round(c / total_calls, 4) if total_calls else 0.0,
        }
        for n, c in sorted(tool_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    po = [r for r in cases if r["produced_output"]]
    pn = [r for r in cases if not r["produced_output"]]

    def gmedian(rs, key):
        return dist([r[key] for r in rs])["median"]

    ending_counts = {}
    for r in cases:
        tag = r["ended_with_tag"] or "unknown"
        ending_counts[tag] = ending_counts.get(tag, 0) + 1

    return {
        "generated_by": "trace_anatomy.py v%s" % VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python_version": sys.version.split()[0],
        "glob_pattern": glob_pattern,
        "runtime_seconds": None if runtime_seconds is None else round(runtime_seconds, 2),
        "coverage": {
            "n_cases": len(cases),
            "n_cases_with_nonempty_session": len(with_session),
            "n_cases_empty_session": len([r for r in cases
                                          if r["session_present"] and r["session_bytes"] == 0]),
            "n_cases_no_session_file": len([r for r in cases if not r["session_present"]]),
            "session_bytes_total": sum(r["session_bytes"] for r in cases),
            "session_lines_total": sum(r["session_lines"] for r in cases),
            "session_bad_lines_total": sum(r["session_bad_lines"] for r in cases),
            "ts_min": min(ts_all) if ts_all else None,
            "ts_max": max(ts_all_end) if ts_all_end else None,
            "outputs_files_total": sum(r["n_output_files_nonempty"] for r in cases),
            "assets_files_total": sum(r["n_asset_files"] for r in cases),
        },
        "distributions_all_cases": {
            "wall_seconds": dist([r["wall_seconds"] for r in cases]),
            "n_iterations": dist([r["n_iterations"] for r in cases]),
            "n_tool_calls": dist([r["n_tool_calls"] for r in cases]),
            "n_output_files": dist([r["n_output_files"] for r in cases]),
            "session_lines": dist([r["session_lines"] for r in cases]),
            "n_reasoning_chunks": dist([r["n_reasoning_chunks"] for r in cases]),
            "n_text_chunks": dist([r["n_text_chunks"] for r in cases]),
            "n_asset_files": dist([r["n_asset_files"] for r in cases]),
        },
        "tool_usage": {
            "n_distinct_tools": len(tool_counts),
            "total_tool_calls": total_calls,
            "mcp_calls": mcp_calls,
            "non_mcp_calls": non_mcp_calls,
            "mcp_call_share": round(mcp_calls / total_calls, 4) if total_calls else 0.0,
            "literal_mcp_prefix_calls": sum(c for n, c in tool_counts.items() if n.startswith("mcp__")),
        },
        "tool_table": tool_table,
        "ending_tag_counts": ending_counts,
        "tokens": {
            "n_with_run_result_aggregate": len([r for r in cases
                                                if r["tokens_source"] == "run_result.aggregateUsage"]),
            "n_tokens_available": len([r for r in cases if r["tokens"]]),
            "sum_output_tokens_where_available": sum((r["tokens"]["output"] or 0)
                                                     for r in cases if r["tokens"]),
            "sum_input_tokens_where_available": sum((r["tokens"]["input"] or 0)
                                                    for r in cases if r["tokens"]),
        },
        "produced_output_groups": {
            "definition": "produced_output = outputs/ 下存在至少 1 个字节数>0 的文件（仅代表产物存在，不代表正确）",
            "true": {
                "n": len(po),
                "median_tool_calls": gmedian(po, "n_tool_calls"),
                "median_wall_seconds": gmedian(po, "wall_seconds"),
                "median_n_output_files": gmedian(po, "n_output_files"),
            },
            "false": {
                "n": len(pn),
                "median_tool_calls": gmedian(pn, "n_tool_calls"),
                "median_wall_seconds": gmedian(pn, "wall_seconds"),
                "median_n_output_files": gmedian(pn, "n_output_files"),
            },
        },
        "cases": cases,
    }



# ---------------------------------------------------------------- Markdown 报告
def _f(v, nd=1):
    if v is None:
        return "—"
    if isinstance(v, float):
        return ("%%.%df" % nd) % v
    return str(v)


def render_md(summary, argv=None):
    c = summary["coverage"]
    d = summary["distributions_all_cases"]
    tu = summary["tool_usage"]
    po = summary["produced_output_groups"]
    L = []
    a = L.append

    a("# Cline 轨迹解剖报告（local48，pilot 子集）")
    a("")
    a("> 本文件的 §1–§7 由 `trace_anatomy.py` **机器生成**，所有数字均可在同一命令下复现。")
    a("> 生成命令：`python trace_anatomy.py --glob \"<cline_eval>/*/cline_session.jsonl\" "
      "--out local48_metrics.json --md <report>.md`")
    a("> argv: `%s`" % (" ".join(argv) if argv else ""))
    a("> 生成时间(UTC)：%s ｜ python %s ｜ 本机总耗时 **%.2f s**"
      % (summary["generated_at"], summary["python_version"], summary["runtime_seconds"] or 0.0))
    a("> 解析器：%s（stdlib only）" % summary["generated_by"])
    a("")

    a("## 1. 覆盖率与规模")
    a("")
    a("| 项目 | 值 |")
    a("| --- | --- |")
    a("| 匹配到的 case 目录数 | %d |" % c["n_cases"])
    a("| 有非空 `cline_session.jsonl` | %d |" % c["n_cases_with_nonempty_session"])
    a("| 有 session 文件但 0 字节 | %d |" % c["n_cases_empty_session"])
    a("| 无 session 文件 | %d |" % c["n_cases_no_session_file"])
    a("| session 总字节 | %d (%.1f MB) |" % (c["session_bytes_total"], c["session_bytes_total"] / 1048576.0))
    a("| session 总行数(事件数) | %d |" % c["session_lines_total"])
    a("| 解析失败行数 | %d |" % c["session_bad_lines_total"])
    a("| 时间跨度(首 ts ~ 末 ts) | %s ~ %s |" % (c["ts_min"], c["ts_max"]))
    a("| outputs/ 非空文件总数 | %d |" % c["outputs_files_total"])
    a("| assets/ 文件总数 | %d |" % c["assets_files_total"])
    a("")

    a("## 2. 分布统计（全部 case，None 值已剔除）")
    a("")
    a("| 指标 | n | median | p25 | p75 | mean | min | max |")
    a("| --- | --- | --- | --- | --- | --- | --- | --- |")
    rows = [("wall_seconds", "wall_seconds (秒)", 1),
            ("n_iterations", "n_iterations", 1),
            ("n_tool_calls", "n_tool_calls", 1),
            ("n_output_files", "n_output_files", 1),
            ("session_lines", "session_lines", 1),
            ("n_reasoning_chunks", "n_reasoning_chunks", 1),
            ("n_text_chunks", "n_text_chunks", 1),
            ("n_asset_files", "n_asset_files", 1)]
    for key, label, nd in rows:
        s = d[key]
        a("| %s | %d | %s | %s | %s | %s | %s | %s |" % (
            label, s["n"], _f(s["median"], nd), _f(s["p25"], nd), _f(s["p75"], nd),
            _f(s["mean"], nd), _f(s["min"], nd), _f(s["max"], nd)))
    a("")
    a("说明：分位数用线性插值（与 numpy 默认 `linear` 口径一致），实现见 `percentile()`。"
      "`n_reasoning_chunks` / `n_text_chunks` 计的是**流式增量 chunk 数**，不是语义段落数——"
      "模型按 token 流式吐字，一个句子会被拆成几十个 chunk，故量级很大。")
    a("")

    a("## 3. 工具使用（top 15）")
    a("")
    a("| # | toolName | 调用次数 | 调用占比 | 出现的 trace 数 (共%d) | 类型 |" %
      c["n_cases_with_nonempty_session"])
    a("| --- | --- | --- | --- | --- | --- |")
    for i, row in enumerate(summary["tool_table"][:15], 1):
        a("| %d | `%s` | %d | %.1f%% | %d | %s |" % (
            i, row["tool"], row["calls"], row["call_share"] * 100, row["traces"],
            "MCP" if row["is_mcp"] else "内置"))
    a("")
    a("| 汇总 | 值 |")
    a("| --- | --- |")
    a("| 不同工具种类数 | %d |" % tu["n_distinct_tools"])
    a("| 工具调用总数 | %d |" % tu["total_tool_calls"])
    a("| MCP 类调用数（名字含 `__`） | %d |" % tu["mcp_calls"])
    a("| 非 MCP 内置调用数 | %d |" % tu["non_mcp_calls"])
    a("| **MCP 调用占比** | **%.1f%%** |" % (tu["mcp_call_share"] * 100))
    a("| 字面 `mcp__` 前缀调用数 | %d |" % tu["literal_mcp_prefix_calls"])
    a("")
    a("MCP 判定口径：Cline 采用 `<server>__<tool>` 命名，故 `\"__\" in toolName` 即视为 MCP server 工具。"
      "本批实际出现的前缀只有 `eda_flow__` 与 `pyAether_MCP_server__`，"
      "**没有任何工具以字面 `mcp__` 开头**（见上表最后一行）。"
      "此外 `tool_call` hook 事件不含工具名，工具名只能从 `agent_event.content_start.contentType==\"tool\"` 取。")
    a("")

    a("## 4. produced_output 分组对比")
    a("")
    a("分组定义：%s" % po["definition"])
    a("")
    a("| 组 | n | median 工具调用数 | median wall_seconds | median n_output_files |")
    a("| --- | --- | --- | --- | --- |")
    a("| produced_output = true | %d | %s | %s | %s |" % (
        po["true"]["n"], _f(po["true"]["median_tool_calls"]),
        _f(po["true"]["median_wall_seconds"]), _f(po["true"]["median_n_output_files"])))
    a("| produced_output = false | %d | %s | %s | %s |" % (
        po["false"]["n"], _f(po["false"]["median_tool_calls"]),
        _f(po["false"]["median_wall_seconds"]), _f(po["false"]["median_n_output_files"])))
    a("")
    a("⚠️ **样本极小（false 组仅 %d 个），且两组按定义互为补集（n_output_files=0 必然落在 false 组），"
      "因此该对比只能当作“行为差异线索”，不能做显著性推断，也不能外推到全量任务集。**"
      % po["false"]["n"])

    a("## 5. 终止形态分布（ended_with_tag）")
    a("")
    a("| ended_with_tag | trace 数 | 含义 |")
    a("| --- | --- | --- |")
    meaning = {
        "completed": "有 `run_result` 且 `finishReason=completed`（正常收尾）",
        "aborted": "有 `run_aborted`（外部/本地中断）或 finishReason=aborted",
        "error": "无 run_result，末条为 `error` 事件（报错收尾）",
        "done_event_only": "有 `done` 事件但缺 `run_result`",
        "no_terminator": "无任何终止记录（采集被截断，最后一行停在 streaming 中途）",
        "empty_session": "`cline_session.jsonl` 为 0 字节",
        "no_session": "目录里没有 `cline_session.jsonl`",
    }
    for tag in sorted(summary["ending_tag_counts"]):
        a("| `%s` | %d | %s |" % (tag, summary["ending_tag_counts"][tag], meaning.get(tag, "")))
    a("")
    a("注意：`no_terminator` 不等于“失败”。它只说明**归档被截断**（harness 侧未落 run_result），"
      "因此这批 trace 的 wall_seconds 是**观测下界**，真实运行时长可能更长。")
    a("")

    a("## 6. token 可得性")
    a("")
    tk = summary["tokens"]
    a("| 项目 | 值 |")
    a("| --- | --- |")
    a("| 有 `run_result.aggregateUsage` 的 trace | %d / %d |" % (tk["n_with_run_result_aggregate"], c["n_cases"]))
    a("| 有任意 token 数字的 trace | %d / %d |" % (tk["n_tokens_available"], c["n_cases"]))
    a("| 可得 trace 的 outputTokens 之和 | %d |" % tk["sum_output_tokens_where_available"])
    a("| 可得 trace 的 inputTokens 之和（aggregate 口径） | %d |" % tk["sum_input_tokens_where_available"])
    a("")
    a("**usage 事件实测字段结构**（本节最需要写清的一点）：")
    a("")
    a("```json")
    a('{"ts":"2026-11-03T05:38:27.285Z","type":"agent_event","event":{"type":"usage",')
    a('  "inputTokens":10797,"outputTokens":110,')
    a('  "totalInputTokens":10797,"totalOutputTokens":110,"totalCost":0}}')
    a("```")
    a("")
    a("```json")
    a('{"ts":"2026-11-04T23:54:25.712Z","type":"run_result","finishReason":"completed","iterations":11,')
    a('  "usage":{"inputTokens":602283,"outputTokens":57143,"cacheReadTokens":0,"cacheWriteTokens":0,"totalCost":0},')
    a('  "aggregateUsage":{"inputTokens":602283,"outputTokens":57143,"cacheReadTokens":0,'
      '"cacheWriteTokens":0,"totalCost":0},')
    a('  "durationMs":608125,"model":{"id":"deepseek-v4-pro-cloud","provider":"openai-compatible"}}')
    a("```")
    a("")
    a("- `usage` 事件：`inputTokens` / `outputTokens` / `totalInputTokens` / `totalOutputTokens` / `totalCost`，"
      "**没有 cacheReadTokens / cacheWriteTokens**；它是**每次请求**的用量，直接求和会重复计入上下文。")
    a("- `run_result.aggregateUsage`：`inputTokens` / `outputTokens` / `cacheReadTokens` / "
      "`cacheWriteTokens` / `totalCost`，是**整个 run 的权威总量**。")
    a("- `tokens` 字段口径：优先 `run_result.aggregateUsage`；缺失时退回 usage 事件求和，"
      "并在 `tokens_source` 标注 `sum(usage events) PER_REQUEST_SUM_NOT_TOTAL`。"
      "48 份里只有 %d 份有可信总量，故本报告**不给 token 分布统计**，避免跨口径混算。"
      % tk["n_with_run_result_aggregate"])
    a("")

    a("## 7. 逐 case 明细")
    a("")
    a("| case_id | bytes | lines | wall_s | iters | tools | out_files | submit_zip | ended | err_sig | tokens_out |")
    a("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in summary["cases"]:
        tok = r["tokens"]["output"] if r["tokens"] else None
        a("| %s | %d | %d | %s | %d | %d | %d | %d | %s | %d | %s |" % (
            r["case_id"].replace("EDA-Eval-DesignFlow-", ""),
            r["session_bytes"], r["session_lines"], _f(r["wall_seconds"]),
            r["n_iterations"], r["n_tool_calls"], r["n_output_files_nonempty"],
            r["submit_attempts"], r["ended_with_tag"] or "-", r["error_signal_total"],
            "—" if tok is None else str(tok)))
    a("")

    a("")


    a("## 8. 字段口径定义")
    a("")
    a("| 字段 | 定义 |")
    a("| --- | --- |")
    a("| `session_bytes` | `cline_session.jsonl` 文件字节数 |")
    a("| `session_lines` | 非空行数（= 解析到的事件对象数）；`session_bad_lines` 为 JSON 解析失败数（本批 0） |")
    a("| `wall_seconds` | 最后一条事件 `ts` − 第一条事件 `ts`（ISO8601 UTC） |")
    a("| `n_iterations` | `agent_event.iteration_start` 计数；`n_iterations_run_result` 为 harness 自报值，用于交叉校验 |")
    a("| `n_tool_calls` | `agent_event.content_start.contentType==\"tool\"` 计数；`n_tool_calls_hook_xcheck` 为 `hook_event.tool_call` 计数，二者应接近 |")
    a("| `tool_histogram` | toolName → 调用次数（来自 content_start(tool)） |")
    a("| `n_reasoning_chunks` / `n_text_chunks` | `content_start` 中 contentType 为 reasoning / text 的**流式 chunk** 计数 |")
    a("| `tokens` | 见 §6 口径 |")
    a("| `submit_attempts` | 工具 `input` 序列化后匹配 `submit\\.zip` 的工具调用次数 |")
    a("| `zip_mention_tool_calls` | 工具 `input` 中出现任意 `*.zip` 路径的工具调用次数 |")
    a("| `n_output_files` | `outputs/` 下文件总数（递归）；`n_output_files_nonempty` 为非空文件数 |")
    a("| `n_asset_files` | `assets/` 下文件总数（递归） |")
    a("| `produced_output` | `n_output_files_nonempty > 0`（产物存在 ≠ 产物正确） |")
    a("| `ended_with_tag` | 见 §5 |")
    a("| `error_signals` | 对 `cline_stderr.log` 全文与“最终文本语料”分别做**不区分大小写** `findall` 计数，"
      "pattern = `error` / `traceback` / `timeout` / `mcp` / `exception` / `failed` / `permission denied`；"
      "`stderr`、`text` 两组分别计数，`total` = 两组之和，`error_signal_total` = 各 pattern 的 total 之和。"
      "最终文本语料取 `run_result.text` → `done.text` → 最后一条 `text.accumulated`（**只取一份**，避免增量重复计数） |")
    a("")
    a("**解析陷阱（实测发现，写下来供后续复用）**：")
    a("")
    a("1. `hook_event.tool_call` / `tool_result` **没有**工具名与内容，只有 ts/agentId/taskId；"
      "工具统计必须走 `agent_event.content_start(contentType=tool)`。")
    a("2. 顶层 `type` 不止 `agent_event` / `hook_event` 两种，还有 `run_result` 与 `run_aborted`；"
      "把它们当 hook_event 处理会把 `hookEventName` 读成 None（本脚本初版就踩过）。")
    a("3. `content_start(text)` 的 `text` 是**增量**，`accumulated` 才是累计；"
      "把 `text` 逐条拼起来等价于 `accumulated`，但两者同时拼就会重复计数。")
    a("4. `content_start(reasoning)` 同理是增量，本报告只用于计数，不用来做文本统计。")
    a("5. `content_end(tool)` 才带 `output` / `durationMs`，偶尔带 `error`（工具执行失败），"
      "已单列为 `n_tool_content_end_errors`。")
    a("")

    a("## 9. 局限（必须与数字一起引用）")
    a("")
    a("1. **没有 judge verdict。** 本批 48 份是 11-05~11-07 pilot 归档，PASS/FAIL 判定不在本地"
      "（不在 session、不在 outputs、不在任何 sidecar 文件里）。因此本报告**只能给行为学指标**"
      "（工具调用、时长、产物是否存在），**不能给通过率、不能做“为什么 PASS/FAIL”的归因**。"
      "下文凡出现“成功/失败”含义的地方，指的都是 `produced_output`（产物文件是否存在），不是判定结果。")
    a("2. **produced_output 是极弱的代理指标**：只要模型写了任意非空文件就为 true——"
      "写错、写一半、写垃圾都算 true；反之 false 只说明 `outputs/` 为空。")
    a("3. **样本小、非随机**：48 份是 pilot 子集，任务类型（EDA 设计流程）与 harness 配置单一，"
      "不可外推到全量集或其它模型。")
    a("4. **archive 截断**：%d 份 trace 无终止记录（`no_terminator` / `empty_session` / `no_session`），"
      "对应 trace 的 `wall_seconds` 是观测下界。"
      % (summary["ending_tag_counts"].get("no_terminator", 0)
         + summary["ending_tag_counts"].get("empty_session", 0)
         + summary["ending_tag_counts"].get("no_session", 0)))
    a("5. **token 覆盖不全**：只有 %d 份有 `run_result.aggregateUsage`，故未给 token 分布。"
      % tk["n_with_run_result_aggregate"])
    a("6. **`error_signals` 是关键词计数**，会把日志里正常的 `**ERROR: (CODE):` 运行输出也算进去，"
      "只适合做量级对比，不宜当失败判据。")
    a("7. **时间戳口径**：本批实测首末 ts 为 2026-11-03 ~ 2026-11-06（UTC），"
      "任务书里写的 11-05~11-07 是批次标签，二者相差 1~2 天；以本文件 §1 的实测区间为准。")
    a("")
    return "\n".join(L) + "\n"



# ---------------------------------------------------------------- 自检 fixture
FIXTURE_LINES = [
    {"ts": "2026-01-01T00:00:00.000Z", "type": "hook_event", "hookEventName": "agent_start",
     "agentId": "a1", "taskId": "t1", "parentAgentId": None},
    {"ts": "2026-01-01T00:00:00.100Z", "type": "agent_event",
     "event": {"type": "iteration_start", "iteration": 1}},
    {"ts": "2026-01-01T00:00:01.000Z", "type": "agent_event",
     "event": {"type": "content_start", "contentType": "reasoning", "reasoning": "Let", "redacted": False}},
    {"ts": "2026-01-01T00:00:01.100Z", "type": "agent_event",
     "event": {"type": "content_start", "contentType": "reasoning", "reasoning": " me", "redacted": False}},
    {"ts": "2026-01-01T00:00:02.000Z", "type": "agent_event",
     "event": {"type": "content_start", "contentType": "text", "text": "Hi", "accumulated": "Hi"}},
    {"ts": "2026-01-01T00:00:03.000Z", "type": "agent_event",
     "event": {"type": "content_start", "contentType": "tool", "toolName": "read_files",
               "toolCallId": "c1", "input": {"files": [{"path": "prompt.txt"}]}}},
    {"ts": "2026-01-01T00:00:03.100Z", "type": "hook_event", "hookEventName": "tool_call",
     "agentId": "a1", "taskId": "t1", "parentAgentId": None},
    {"ts": "2026-01-01T00:00:03.200Z", "type": "hook_event", "hookEventName": "tool_result",
     "agentId": "a1", "taskId": "t1", "parentAgentId": None},
    {"ts": "2026-01-01T00:00:03.300Z", "type": "agent_event",
     "event": {"type": "content_end", "contentType": "tool", "toolName": "read_files",
               "toolCallId": "c1", "output": "ok", "durationMs": 12}},
    {"ts": "2026-01-01T00:00:04.000Z", "type": "agent_event",
     "event": {"type": "usage", "inputTokens": 100, "outputTokens": 10,
               "totalInputTokens": 100, "totalOutputTokens": 10, "totalCost": 0}},
    {"ts": "2026-01-01T00:00:04.100Z", "type": "agent_event",
     "event": {"type": "iteration_end", "iteration": 1, "hadToolCalls": True, "toolCallCount": 1}},
    {"ts": "2026-01-01T00:00:05.000Z", "type": "agent_event",
     "event": {"type": "iteration_start", "iteration": 2}},
    {"ts": "2026-01-01T00:00:06.000Z", "type": "agent_event",
     "event": {"type": "content_start", "contentType": "tool", "toolName": "eda_flow__write_file",
               "toolCallId": "c2", "input": {"path": "outputs/submit.zip", "content": "x"}}},
    {"ts": "2026-01-01T00:00:20.000Z", "type": "agent_event",
     "event": {"type": "content_start", "contentType": "tool", "toolName": "eda_flow__declare_done",
               "toolCallId": "c3", "input": {}}},
    {"ts": "2026-01-01T00:00:21.000Z", "type": "agent_event",
     "event": {"type": "usage", "inputTokens": 200, "outputTokens": 10,
               "totalInputTokens": 200, "totalOutputTokens": 10, "totalCost": 0}},
    {"ts": "2026-01-01T00:00:22.000Z", "type": "agent_event",
     "event": {"type": "notice", "noticeType": "status", "displayRole": "status",
               "message": "auto-compacting", "reason": "auto_compaction",
               "metadata": {"kind": "auto_compaction", "phase": "started", "iteration": 2}}},
    {"ts": "2026-01-01T00:00:30.000Z", "type": "agent_event",
     "event": {"type": "content_start", "contentType": "text", "text": " done", "accumulated": "Hi done"}},
    {"ts": "2026-01-01T00:00:59.000Z", "type": "agent_event",
     "event": {"type": "done", "reason": "completed", "iterations": 2,
               "usage": {"inputTokens": 300, "outputTokens": 20, "totalCost": 0.01},
               "text": "Hi done"}},
    {"ts": "2026-01-01T00:01:00.000Z", "type": "run_result", "finishReason": "completed",
     "iterations": 2,
     "usage": {"inputTokens": 300, "outputTokens": 20, "cacheReadTokens": 5,
               "cacheWriteTokens": 6, "totalCost": 0.01},
     "aggregateUsage": {"inputTokens": 300, "outputTokens": 20, "cacheReadTokens": 5,
                        "cacheWriteTokens": 6, "totalCost": 0.01},
     "durationMs": 60000, "model": {"id": "test-model", "provider": "openai-compatible"},
     "text": "Error: done. submit.zip written."},
]


def _build_fixture(root):
    """构造 2 个 case：FIX-001 完整、FIX-002 空 session。"""
    c1 = os.path.join(root, "FIX-001")
    os.makedirs(os.path.join(c1, "outputs"))
    os.makedirs(os.path.join(c1, "assets"))
    with open(os.path.join(c1, "cline_session.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for o in FIXTURE_LINES:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    with open(os.path.join(c1, "cline_stderr.log"), "w", encoding="utf-8", newline="\n") as f:
        f.write("Error: boom\nMCP server ready\nTraceback (most recent call last):\n")
    with open(os.path.join(c1, "outputs", "out.py"), "w", encoding="utf-8", newline="\n") as f:
        f.write("print(1)\n")
    open(os.path.join(c1, "outputs", "empty.txt"), "w").close()   # 0 字节，不计入非空
    with open(os.path.join(c1, "outputs", "submit.zip"), "wb") as f:
        f.write(b"PK\x03\x04fake")
    with open(os.path.join(c1, "assets", "in.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("asset\n")

    c2 = os.path.join(root, "FIX-002")
    os.makedirs(os.path.join(c2, "outputs"))
    os.makedirs(os.path.join(c2, "assets"))
    open(os.path.join(c2, "cline_session.jsonl"), "w").close()      # 0 字节
    with open(os.path.join(c2, "cline_stderr.log"), "w", encoding="utf-8", newline="\n") as f:
        f.write("no fixture issues\n")
    return c1, c2


def run_selftest():
    """unittest 风格自检：构造小 fixture 断言各解析字段。"""
    import shutil
    import tempfile
    import unittest

    class AnatomyTest(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.tmp = tempfile.mkdtemp(prefix="trace_anatomy_fixture_")
            c1, c2 = _build_fixture(cls.tmp)
            cls.c1, cls.c2 = c1, c2
            cls.r1 = analyze_case(os.path.join(c1, "cline_session.jsonl"))
            cls.r2 = analyze_case(os.path.join(c2, "cline_session.jsonl"))

        @classmethod
        def tearDownClass(cls):
            shutil.rmtree(cls.tmp, ignore_errors=True)

        # -- 基础规模
        def test_case_id_and_lines(self):
            self.assertEqual(self.r1["case_id"], "FIX-001")
            self.assertTrue(self.r1["session_present"])
            self.assertGreater(self.r1["session_bytes"], 0)
            self.assertEqual(self.r1["session_lines"], len(FIXTURE_LINES))
            self.assertEqual(self.r1["session_bad_lines"], 0)

        def test_wall_seconds(self):
            self.assertEqual(self.r1["ts_first"], "2026-01-01T00:00:00.000Z")
            self.assertEqual(self.r1["ts_last"], "2026-01-01T00:01:00.000Z")
            self.assertAlmostEqual(self.r1["wall_seconds"], 60.0, places=3)

        # -- 行为计数
        def test_iterations_and_tools(self):
            self.assertEqual(self.r1["n_iterations"], 2)
            self.assertEqual(self.r1["n_iterations_run_result"], 2)
            self.assertEqual(self.r1["n_tool_calls"], 3)
            self.assertEqual(self.r1["n_tool_calls_hook_xcheck"], 1)  # hook 侧只有 1 个 tool_call
            self.assertEqual(self.r1["tool_histogram"], {
                "eda_flow__declare_done": 1,
                "eda_flow__write_file": 1,
                "read_files": 1,
            })

        def test_chunk_counts(self):
            self.assertEqual(self.r1["n_reasoning_chunks"], 2)
            self.assertEqual(self.r1["n_text_chunks"], 2)
            self.assertEqual(self.r1["reasoning_chars"], len("Let me"))

        def test_submit_detection(self):
            self.assertEqual(self.r1["submit_attempts"], 1)
            self.assertEqual(self.r1["zip_mention_tool_calls"], 1)
            self.assertEqual(self.r1["n_declare_done_tool_calls"], 1)

        # -- token 口径
        def test_tokens_from_aggregate_usage(self):
            self.assertEqual(self.r1["tokens_source"], "run_result.aggregateUsage")
            tk = self.r1["tokens"]
            self.assertEqual(tk["input"], 300)
            self.assertEqual(tk["output"], 20)
            self.assertEqual(tk["cache_read"], 5)
            self.assertEqual(tk["cache_write"], 6)
            self.assertEqual(self.r1["n_usage_events"], 2)

        # -- 目录侧
        def test_output_and_asset_dirs(self):
            self.assertEqual(self.r1["n_output_files"], 3)            # out.py + empty.txt + submit.zip
            self.assertEqual(self.r1["n_output_files_nonempty"], 2)   # 0 字节文件被排除
            self.assertTrue(self.r1["produced_output"])
            self.assertTrue(self.r1["has_zip_in_outputs"])
            self.assertEqual(self.r1["n_asset_files"], 1)

        # -- 终止形态与事件
        def test_ending_and_events(self):
            self.assertEqual(self.r1["ended_with_tag"], "completed")
            self.assertEqual(self.r1["finish_reason"], "completed")
            self.assertEqual(self.r1["n_done_events"], 1)
            self.assertEqual(self.r1["n_auto_compactions"], 1)
            self.assertEqual(self.r1["n_notices"], 1)
            self.assertEqual(self.r1["n_error_events"], 0)
            self.assertEqual(self.r1["final_text_source"], "run_result.text")
            self.assertEqual(self.r1["text_chars_final"], len("Error: done. submit.zip written."))

        # -- 错误信号（stderr 与 文本 分别计数）
        def test_error_signals(self):
            es = self.r1["error_signals"]
            self.assertEqual(es["stderr"]["error"], 1)
            self.assertEqual(es["stderr"]["mcp"], 1)
            self.assertEqual(es["stderr"]["traceback"], 1)
            self.assertEqual(es["stderr"]["timeout"], 0)
            self.assertEqual(es["text"]["error"], 1)
            self.assertEqual(es["total"]["error"], 2)     # stderr 1 + 文本 1
            self.assertEqual(self.r1["error_signal_total"], sum(es["total"].values()))

        # -- 空 session 退化路径
        def test_empty_session_case(self):
            self.assertEqual(self.r2["ended_with_tag"], "empty_session")
            self.assertEqual(self.r2["session_lines"], 0)
            self.assertIsNone(self.r2["wall_seconds"])
            self.assertIsNone(self.r2["tokens"])
            self.assertEqual(self.r2["n_tool_calls"], 0)
            self.assertFalse(self.r2["produced_output"])

        # -- 统计工具
        def test_percentile_and_dist(self):
            self.assertAlmostEqual(percentile([1, 2, 3, 4], 25), 1.75, places=6)
            self.assertAlmostEqual(percentile([1, 2, 3, 4], 50), 2.5, places=6)
            self.assertAlmostEqual(percentile([1, 2, 3, 4], 75), 3.25, places=6)
            d = dist([1, 2, 3, 4])
            self.assertEqual(d["min"], 1.0)
            self.assertEqual(d["max"], 4.0)
            self.assertAlmostEqual(d["mean"], 2.5, places=6)
            self.assertEqual(dist([None, None])["n"], 0)

        def test_mcp_classification(self):
            self.assertTrue(is_mcp_tool("eda_flow__run_commands"))
            self.assertTrue(is_mcp_tool("pyAether_MCP_server__run_code"))
            self.assertTrue(is_mcp_tool("mcp__foo__bar"))
            self.assertFalse(is_mcp_tool("read_files"))
            self.assertFalse(is_mcp_tool("editor"))

        # -- 聚合 + Markdown 渲染
        def test_aggregate(self):
            s = aggregate([self.r1, self.r2], runtime_seconds=0.5, glob_pattern="fixture")
            self.assertEqual(s["coverage"]["n_cases"], 2)
            self.assertEqual(s["coverage"]["n_cases_with_nonempty_session"], 1)
            self.assertEqual(s["coverage"]["n_cases_empty_session"], 1)
            self.assertEqual(s["tool_usage"]["total_tool_calls"], 3)
            self.assertEqual(s["tool_usage"]["mcp_calls"], 2)
            self.assertEqual(s["tool_usage"]["non_mcp_calls"], 1)
            self.assertAlmostEqual(s["tool_usage"]["mcp_call_share"], 2 / 3.0, places=4)
            self.assertEqual(s["tool_usage"]["literal_mcp_prefix_calls"], 0)
            self.assertEqual(s["produced_output_groups"]["true"]["n"], 1)
            self.assertEqual(s["produced_output_groups"]["false"]["n"], 1)
            self.assertEqual(s["ending_tag_counts"].get("completed"), 1)
            self.assertEqual(s["ending_tag_counts"].get("empty_session"), 1)
            md = render_md(s, argv=["selftest"])
            self.assertIn("## 9. 局限", md)
            self.assertIn("produced_output", md)

    suite = unittest.TestLoader().loadTestsFromTestCase(AnatomyTest)
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    return 0 if result.wasSuccessful() else 1


    with open(os.path.join(c1, "assets", "in.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("asset\n")

    c2 = os.path.join(root, "FIX-002")
    os.makedirs(os.path.join(c2, "outputs"))
    os.makedirs(os.path.join(c2, "assets"))
    open(os.path.join(c2, "cline_session.jsonl"), "w").close()    # 0 字节


# ---------------------------------------------------------------- 入口
def expand_targets(pattern):
    """展开 --glob；匹配到目录则拼 cline_session.jsonl；去重排序。"""
    matched = sorted(glob.glob(pattern))
    paths = []
    seen = set()
    for p in matched:
        cand = os.path.join(p, "cline_session.jsonl") if os.path.isdir(p) else p
        key = os.path.normcase(os.path.abspath(cand))
        if key in seen:
            continue
        seen.add(key)
        paths.append(cand)
    return paths


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description="Cline trace anatomy analyzer (stdlib only)")
    ap.add_argument("--glob", dest="pattern", default=None,
                    help="匹配 cline_session.jsonl 或 case 目录的 glob")
    ap.add_argument("--out", dest="out", default=None, help="输出 metrics.json 路径")
    ap.add_argument("--md", dest="md", default=None, help="可选：同时输出 Markdown 报告")
    ap.add_argument("--selftest", action="store_true", help="运行内建 fixture 自检")
    ap.add_argument("--quiet", action="store_true", help="不打印逐 case 进度")
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest()
    if not args.pattern:
        ap.error("--glob 必填（或用 --selftest）")
    if not args.out:
        ap.error("--out 必填（或用 --selftest）")

    targets = expand_targets(args.pattern)
    if not targets:
        sys.stderr.write("ERROR: --glob 无匹配: %s\n" % args.pattern)
        return 2

    t0 = time.time()
    records = []
    for i, path in enumerate(targets, 1):
        rec = analyze_case(path)
        records.append(rec)
        if not args.quiet:
            sys.stdout.write("[%3d/%3d] %-46s lines=%-7d tools=%-4d wall=%-9s out=%d %s\n" % (
                i, len(targets), rec["case_id"], rec["session_lines"],
                rec["n_tool_calls"], rec["wall_seconds"], rec["n_output_files_nonempty"],
                rec["ended_with_tag"]))
            sys.stdout.flush()
    runtime = time.time() - t0

    summary = aggregate(records, runtime_seconds=runtime, glob_pattern=args.pattern)

    out_path = os.path.abspath(args.out)
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
        f.write("\n")

    if args.md:
        md_path = os.path.abspath(args.md)
        md_dir = os.path.dirname(md_path)
        if md_dir and not os.path.isdir(md_dir):
            os.makedirs(md_dir)
        with open(md_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(render_md(summary, argv=["trace_anatomy.py"] + argv))

    c = summary["coverage"]
    sys.stdout.write(
        "\nDONE %d cases (%d with non-empty session) | %d bytes | %d lines | %.2f s\n"
        "     -> %s\n" % (c["n_cases"], c["n_cases_with_nonempty_session"],
                          c["session_bytes_total"], c["session_lines_total"], runtime, out_path))
    if args.md:
        sys.stdout.write("     -> %s\n" % os.path.abspath(args.md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
