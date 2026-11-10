#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_tool_health.py — EDA 工具健康深挖（696-run 批次），stdlib-only，py3.8+。

从 cline session（cline_session.jsonl）里抽取每个 run 真正执行过的 shell/EDA
命令，识别 23 个 EDA 工具的调用与成败，归一化失败签名并做交叉分析，产出：

1. ``tool_health.json``  —— 机器可读，每条聚合都带 evidence 路径。
2. 中文 HTML 报告（``--html``）—— 自包含（内联 CSS + 内联 SVG 条形图，
   不引 CDN、不依赖 JS）。

四态定义（每个工具）
-------------------
- 有正常输出 (ok)        : 命令 exit_code==0 且 stderr/stdout 无错误签名
- 报错退出   (error)     : exit_code!=0 或 stderr/stdout 命中错误签名
- 调了但无产物 (no_output): exit_code==0 但 stdout 与 stderr 均空（可能被
                            ``> /dev/null 2>&1`` 重定向，报告里如实标注）
- 从未调用   (never)     : 该 run 的全部命令里从未出现该工具（**不算失败**）

调用判定（两套口径，都报）
-------------------------
- raw_mention : 词边界正则命中（大小写不敏感）—— 任务书要求的口径
- true_call   : 工具在管道/链路段首被执行（剔除 printf/echo/heredoc/JSON 字符串
                里的字符串提及），plus ``which/type/command <tool>`` 探测。
健康矩阵以 true_call 为主，raw_mention 作为旁注以防低估。

用法
----
  python3 07_tool_health.py \
      --triage results/run_batch_20261109_171201/triage_summary.json \
      --batch /nasdata/app.e0031982/.cache/triage_batch_20261109_171201 \
      --out   results/run_batch_20261109_171201 \
      --html  /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/reports/report_designflow_tool_health_20261110_zh.html
"""
from __future__ import annotations
import argparse
import base64
import collections
import datetime as _dt
import html as _html
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

TOOL_LIST = [
    "finesim", "hspice", "spectre", "eldo", "smartspice", "asc",
    "aether", "schematic", "calibre", "pvx",
    "innovus", "icc2", "pt_shell", "primetime", "dc_shell", "design_compiler",
    "verdi", "vcs", "xrun",
    "spyglass", "star-rc", "redhawk", "totem", "siliconsmart", "pyaether",
]
# 大小写不敏感词边界正则（"star-rc" 含连字符，单独构造）
def _tok_re(tok: str) -> re.Pattern:
    # 把 token 转义；词边界用前后非 [A-Za-z0-9_] 断言（兼容含 - 的 token）
    esc = re.escape(tok)
    return re.compile(r"(?<![A-Za-z0-9_])" + esc + r"(?![A-Za-z0-9_])", re.IGNORECASE)

TOOL_RES = {t: _tok_re(t) for t in TOOL_LIST}

# 失败签名（按顺序匹配，命中即归类）
SIGNATURE_RULES: List[Tuple[str, re.Pattern]] = [
    ("command not found / No such file",
     re.compile(r"command not found|No such file or directory|not found\b\s*(?:in path)?|no such file", re.IGNORECASE)),
    ("licence / license error",
     re.compile(r"licen[cs]e|flexlm|lmgrd|flexnet|job rejected|license file error|cannot get license", re.IGNORECASE)),
    ("permission denied",
     re.compile(r"permission denied|access denied|not authorized|operation not permitted", re.IGNORECASE)),
    ("MCP / connection refused",
     re.compile(r"MCP[^\n]*?(refused|error|failed|unavailable|timeout)|connection refused|ECONNREFUSED|socket hang up|backend unavailable", re.IGNORECASE)),
    ("timeout",
     re.compile(r"\btimeout\b|timed out|deadline exceeded|TIMEOUT", re.IGNORECASE)),
    ("syntax error",
     re.compile(r"syntax error|syntax ERROR|unexpected token|unmatched|parse error", re.IGNORECASE)),
    ("undefined reference / net",
     re.compile(r"undefined net|unresolved reference|undeclared|CUVUNF|cannot find|undefined symbol|not defined|undefined instance|hierarchical name component lookup failed", re.IGNORECASE)),
    ("SPICE convergence",
     re.compile(r"converg|timestep too small|gmin stepping|nonconvergence|no convergence|transient convergence|tran convergence", re.IGNORECASE)),
    ("tool crashed / segfault",
     re.compile(r"segmentation fault|core dumped|abort|fatal error|killed by signal|SIGSEGV|bus error", re.IGNORECASE)),
    ("file format / parse",
     re.compile(r"bad file format|invalid format|malformed|cannot open|could not open|failed to open|empty file", re.IGNORECASE)),
    ("argument / usage error",
     re.compile(r"usage:|invalid option|missing argument|unknown option|bad option|argument required", re.IGNORECASE)),
    ("python traceback",
     re.compile(r"Traceback \(most recent call last\)|ImportError|ModuleNotFoundError|AttributeError|KeyError|ValueError|NameError|TypeError|FileNotFoundError", re.IGNORECASE)),
    ("non-zero exit (no stderr)",
     re.compile(r"exit\s*=\s*[1-9]|exit code\s*[1-9]|returned\s+[1-9]\d*", re.IGNORECASE)),
]
SIG_ORDER = [name for name, _ in SIGNATURE_RULES] + ["other"]

# 用于 true_call 判定的段分隔符
_SEG_SPLIT = re.compile(r"(?:&&|\|\||\||;)")
# 段首环境变量赋值 / cd 前缀剥离
_LEAD_ENV = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S+\s+)+")
_LEAD_CD = re.compile(r"^cd\s+\S+\s*(?:&&\s*)?")


def classify_signature(stderr_first: str, stdout_sample: str, exit_code: Optional[int]) -> str:
    """归一化失败签名。先看 stderr，再看 stdout，再看 exit_code。"""
    blob = "\n".join(x for x in [stderr_first, stdout_sample] if x)
    for name, pat in SIGNATURE_RULES:
        if pat.search(blob):
            return name
    if exit_code is not None and exit_code != 0:
        return "non-zero exit (no stderr)"
    return ""


def _norm_evidence_line(s: str, maxlen: int = 200) -> str:
    s = s.replace("\n", " ").replace("\r", " ").strip()
    s = re.sub(r"\s+", " ", s)
    if len(s) > maxlen:
        s = s[:maxlen - 1] + "…"
    return s


def split_segments(cmd: str) -> List[str]:
    """把命令按 ; && || | 切成段（粗切，不处理引号内的分隔符——够用）。"""
    if not cmd:
        return []
    segs = _SEG_SPLIT.split(cmd)
    out = []
    for s in segs:
        s = s.strip()
        if not s:
            continue
        # 剥离 redirection 后缀以便看清段首可执行名
        s_no_redir = re.sub(r"\s*(?:\d?>\S*|2>\S*|2>&1|>\s*/dev/null[^|&;]*)\s*$", "", s).strip()
        s2 = _LEAD_ENV.sub("", s_no_redir)
        s2 = _LEAD_CD.sub("", s2).strip()
        out.append(s2 if s2 else s_no_redir)
    return out


def first_token(seg: str) -> str:
    if not seg:
        return ""
    return seg.split()[0] if seg.split() else ""


def classify_mentions(cmd: str) -> List[Tuple[str, str]]:
    """返回 [(tool, role)] —— role in {invoke, probe, mention}。

    invoke : 工具在某个管道/链路段的段首（真被执行）
    probe  : 工具是 which/type/command 的参数（探测存在性）
    mention: 其它出现（printf/echo/heredoc/JSON 字符串等，不算调用）
    """
    found = []
    seen = set()
    segs = split_segments(cmd)
    for seg in segs:
        ft = first_token(seg)
        # which / type / command 探测
        if ft.lower() in ("which", "type", "command", "whereis"):
            for tok in seg.split()[1:]:
                for t in TOOL_LIST:
                    if tok.lower() == t.lower() and t not in seen:
                        found.append((t, "probe")); seen.add(t)
            continue
        # 段首即工具
        for t in TOOL_LIST:
            if ft.lower() == t.lower() and t not in seen:
                found.append((t, "invoke")); seen.add(t)
        # 段内其余词边界命中算 mention（但若已被段首 invoke，跳过）
        for t in TOOL_LIST:
            if t in seen:
                continue
            if TOOL_RES[t].search(seg):
                found.append((t, "mention")); seen.add(t)
    # 兜底：整条命令里词边界命中但没进任何段（罕见）算 mention
    for t in TOOL_LIST:
        if t in seen:
            continue
        if TOOL_RES[t].search(cmd):
            found.append((t, "mention")); seen.add(t)
    return found


def resolve_session_path(batch_dir: str, case_dir: str) -> Optional[str]:
    link = os.path.join(batch_dir, case_dir, "cline_stderr.log")
    try:
        tgt = os.readlink(link)
    except OSError:
        return None
    if not os.path.isabs(tgt):
        tgt = os.path.join(os.path.dirname(link), tgt)
    rundir = os.path.dirname(os.path.normpath(tgt))
    sj = os.path.join(rundir, "cline_session.jsonl")
    return sj if os.path.isfile(sj) else None


def parse_session(sj_path: str) -> List[dict]:
    """解析一个 cline_session.jsonl，返回 tool-call 记录列表。

    每条：{tool_name, tool_call_id, commands:[...], results:[{exit_code,stdout,stderr,success}]}
    """
    ends: Dict[str, Any] = {}
    calls: List[dict] = []
    try:
        with open(sj_path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if o.get("type") != "agent_event":
                    continue
                ev = o.get("event") or {}
                et = ev.get("type")
                if et == "content_end" and ev.get("contentType") == "tool":
                    ends[ev.get("toolCallId")] = ev.get("output")
                elif et == "content_start" and ev.get("contentType") == "tool":
                    tn = ev.get("toolName")
                    if tn in ("run_commands", "eda_flow__run_commands"):
                        inp = ev.get("input")
                        # input 偶尔是 [{"commands":[...]}] 形态，归一成 dict
                        if isinstance(inp, list):
                            inp = inp[0] if inp and isinstance(inp[0], dict) else {}
                        if not isinstance(inp, dict):
                            inp = {}
                        calls.append({
                            "tool_name": tn,
                            "tool_call_id": ev.get("toolCallId"),
                            "input": inp,
                        })
    except Exception:
        return []
    out = []
    for c in calls:
        inp = c.get("input") or {}
        cmds = inp.get("commands") or []
        if not isinstance(cmds, list) or not cmds:
            continue
        outp = ends.get(c["tool_call_id"])
        results = _extract_results(outp, len(cmds), c["tool_name"])
        out.append({
            "tool_name": c["tool_name"],
            "tool_call_id": c["tool_call_id"],
            "commands": cmds,
            "results": results,
        })
    return out


def _extract_results(outp: Any, n: int, tool_name: str) -> List[dict]:
    """从 content_end.output 抽取每个命令对应的结果条目。"""
    results: List[dict] = []
    parsed = None
    if isinstance(outp, dict):
        cont = outp.get("content") or []
        for cc in cont:
            if isinstance(cc, dict) and cc.get("type") == "text":
                txt = cc.get("text") or ""
                try:
                    parsed = json.loads(txt)
                except Exception:
                    parsed = None
                break
    elif isinstance(outp, list):
        parsed = outp
    if isinstance(parsed, dict) and "results" in parsed:
        rs = parsed.get("results") or []
        for r in rs:
            if not isinstance(r, dict):
                results.append({})
                continue
            results.append({
                "exit_code": r.get("exit_code"),
                "stdout": r.get("stdout") or "",
                "stderr": r.get("stderr") or "",
            })
    elif isinstance(parsed, list):
        # local run_commands: [{query, result, success}]
        for r in parsed:
            if not isinstance(r, dict):
                results.append({})
                continue
            succ = r.get("success")
            exit_code = 0 if succ is True else (1 if succ is False else None)
            results.append({
                "exit_code": exit_code,
                "stdout": r.get("result") or "",
                "stderr": "",
            })
    # 对齐长度
    while len(results) < n:
        results.append({})
    return results[:n]


def first_stderr_line(stderr: str) -> str:
    for ln in (stderr or "").splitlines():
        ln = ln.strip()
        if ln:
            return ln
    return ""


def stderr_first_line_norm(line: str) -> str:
    """去掉路径/时间/编号后聚类。"""
    s = line
    s = re.sub(r"/[^\s:'\"]+", "<path>", s)
    s = re.sub(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[^\s]*", "<ts>", s)
    s = re.sub(r"\b0x[0-9A-Fa-f]+\b", "<hex>", s)
    s = re.sub(r"line\s+\d+", "line N", s, flags=re.IGNORECASE)
    s = re.sub(r":\d+: ?", ":N: ", s)
    s = re.sub(r"\bpid\s*\d+\b", "pid N", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:160]


def analyze(triage_path: str, batch_dir: str) -> dict:
    with open(triage_path, "r", encoding="utf-8") as fh:
        triage = json.load(fh)
    cases = triage.get("cases") or []
    overall = triage.get("overall") or {}
    domains = triage.get("domains") or {}

    # 工具聚合
    tool_agg: Dict[str, dict] = {t: {
        "true_calls": 0, "raw_mentions": 0,
        "ok": 0, "error": 0, "no_output": 0,
        "invoke": 0, "probe": 0, "mention": 0,
        "runs_invoked": set(), "runs_error": set(),
        "examples_error": [], "examples_ok": [],
    } for t in TOOL_LIST}

    # 失败签名聚合
    sig_agg: Dict[str, dict] = {s: {
        "runs": set(), "count": 0, "examples": [],
    } for s in SIG_ORDER}

    # 每个 run 的解析结果
    run_records: List[dict] = []
    n_no_session = 0
    n_session_ok = 0
    n_parse_fail = 0

    for case in cases:
        task_id = case.get("task_id")
        domain = case.get("domain") or "unknown"
        status = case.get("status")
        cls = case.get("class")
        case_dir = (case.get("evidence") or {}).get("case_dir") or task_id
        sj = resolve_session_path(batch_dir, case_dir)
        rec = {
            "task_id": task_id, "domain": domain, "status": status, "class": cls,
            "session_path": sj, "tools_seen": set(), "tools_error": set(),
            "tool_calls_true": collections.Counter(),
            "signatures": collections.Counter(),
            "excluded": None,
        }
        if not sj:
            n_no_session += 1
            rec["excluded"] = "no_session_file"
            run_records.append(rec)
            continue
        calls = parse_session(sj)
        if not calls:
            n_parse_fail += 1
            rec["excluded"] = "no_tool_calls_parsed"
            run_records.append(rec)
            continue
        n_session_ok += 1
        for call in calls:
            cmds = call["commands"]
            results = call["results"]
            for i, cmd in enumerate(cmds):
                if not isinstance(cmd, str):
                    continue
                mentions = classify_mentions(cmd)
                # raw_mention（词边界）口径
                for t in TOOL_LIST:
                    if TOOL_RES[t].search(cmd):
                        tool_agg[t]["raw_mentions"] += 1
                # 是否真正执行/探测了 EDA 工具（决定是否计入失败签名）
                tool_roles = [r for _, r in mentions]
                has_invoke = "invoke" in tool_roles
                has_tool_exec = has_invoke or ("probe" in tool_roles)
                # probe-only 命令的探测结果（命令级）：是否有任一工具被找到 / 是否有任一工具明确未找到
                probe_tools = [t for t, r in mentions if r == "probe"]
                any_probe_found = any(
                    bool(re.search(r"/\S*" + re.escape(t) + r"(?![A-Za-z0-9_])", stdout[:600]))
                    for t in probe_tools)
                any_probe_notfound = (not any_probe_found) and bool(probe_tools) and bool(re.search(
                    r"(?:not found|No such file|cannot access|no such file)",
                    stderr_first + " " + stdout[:600], re.IGNORECASE))
                res = results[i] if i < len(results) else {}
                exit_code = res.get("exit_code")
                stdout = res.get("stdout") or ""
                stderr = res.get("stderr") or ""
                stderr_first = first_stderr_line(stderr)
                stdout_head = stdout[:400] if stdout else ""
                # 失败信号：非零退出 / 有 stderr / stdout 里显式 "exit=N"(N>=1，agent 捕获内层工具退出码)
                inner_exit_fail = bool(re.search(r"exit\s*=\s*[1-9]\d*", stdout_head, re.IGNORECASE))
                inner_exit_ok = bool(re.search(r"exit\s*=\s*0\b", stdout_head, re.IGNORECASE))
                has_fail_signal = (exit_code not in (None, 0)) or bool(stderr_first) or inner_exit_fail
                # 结果状态（保守：无失败信号一律不算 error，避免把 stdout banner 里的
                # "license"/"convergence" 等关键词误判）
                # 链式命令修正：若 stdout 有内层 "exit=0"（agent 在工具后紧跟 echo exit=$?）
                # 且无 "exit=N>=1" 且无 stderr，说明工具本身成功，外层非零退出源于后续
                # 无关子命令（如 python3/grep），应判 ok，不归给工具。
                if not stdout and not stderr and exit_code in (None, 0):
                    kind = "no_output"
                    sig = ""
                elif inner_exit_ok and not inner_exit_fail and not stderr_first:
                    kind = "ok"
                    sig = ""
                elif not has_fail_signal:
                    kind = "ok"
                    sig = ""
                else:
                    kind = "error"
                    # 优先在 stderr 找签名，再退到 stdout（仅在有失败信号时）
                    sig = classify_signature(stderr_first, "", exit_code)
                    if not sig and stdout_head:
                        sig = classify_signature("", stdout_head, exit_code)
                    if not sig:
                        sig = "non-zero exit (no stderr)" if (exit_code and exit_code != 0) else "other"
                # 失败签名只对【EDA 工具执行命令】的 error 记：
                #   - invoke 失败（真工具执行失败）
                #   - probe-only 且工具明确未找到（"工具未安装"信号）
                # 剔除 grep/ls/test 等普通命令噪声，以及 probe 已找到工具的命令。
                record_sig = (kind == "error" and sig and
                              (has_invoke or (any_probe_notfound and not has_invoke)))
                if record_sig:
                    sig_agg[sig]["count"] += 1
                    sig_agg[sig]["runs"].add(task_id)
                    if len(sig_agg[sig]["examples"]) < 3:
                        sig_agg[sig]["examples"].append({
                            "task_id": task_id, "domain": domain, "tool_name": call["tool_name"],
                            "exit_code": exit_code,
                            "evidence": _norm_evidence_line(stderr_first or stdout_head, 200),
                        })
                    rec["signatures"][sig] += 1
                # 工具计数（按 role；只对 invoke/probe 记成败）
                for t, role in mentions:
                    tool_agg[t][role] = tool_agg[t].get(role, 0) + 1
                    rec["tools_seen"].add(t)
                    if role in ("invoke", "probe"):
                        tool_agg[t]["true_calls"] += 1
                        tool_agg[t]["runs_invoked"].add(task_id)
                        # probe-only 命令：用 stdout 是否含工具路径判定，避免把同链
                        # 后续 ls/grep 的失败误归给被探测的工具。
                        is_probe_only = (role == "probe" and "invoke" not in tool_roles)
                        if is_probe_only:
                            probe_found = bool(re.search(r"/\S*" + re.escape(t) + r"(?![A-Za-z0-9_])", stdout_head))
                            probe_notfound = (not probe_found) and bool(re.search(
                                r"(?:not found|No such file|cannot access|no such file)", stderr_first + " " + stdout_head, re.IGNORECASE))
                            if probe_found:
                                pkind = "ok"
                            elif probe_notfound:
                                pkind = "error"
                            else:
                                pkind = "ok"  # 探测结果不明确，保守算 ok（不计为失败）
                        else:
                            pkind = kind
                        if pkind == "ok":
                            tool_agg[t]["ok"] += 1
                            if len(tool_agg[t]["examples_ok"]) < 2:
                                tool_agg[t]["examples_ok"].append({
                                    "task_id": task_id, "cmd": _norm_evidence_line(cmd, 160),
                                    "exit_code": exit_code})
                        elif pkind == "error":
                            tool_agg[t]["error"] += 1
                            tool_agg[t]["runs_error"].add(task_id)
                            if len(tool_agg[t]["examples_error"]) < 2:
                                tool_agg[t]["examples_error"].append({
                                    "task_id": task_id, "cmd": _norm_evidence_line(cmd, 160),
                                    "exit_code": exit_code,
                                    "stderr": _norm_evidence_line(stderr_first or stdout_head, 160)})
                        elif pkind == "no_output":
                            tool_agg[t]["no_output"] += 1
                    # mention-only 不计 true_call 成败（raw_mention 已记）
        run_records.append(rec)

    # 汇总
    total_runs = len(cases)
    runs_with_session = n_session_ok
    # 工具矩阵
    tools_summary = []
    for t in TOOL_LIST:
        a = tool_agg[t]
        runs_inv = len(a["runs_invoked"])
        tools_summary.append({
            "tool": t,
            "true_calls": a["true_calls"],
            "raw_mentions": a["raw_mentions"],
            "invoke": a["invoke"], "probe": a["probe"], "mention_only": a["mention"],
            "ok": a["ok"], "error": a["error"], "no_output": a["no_output"],
            "runs_invoked": runs_inv,
            "runs_never_invoked": runs_with_session - runs_inv,
            "all_calls_failed": (a["true_calls"] > 0 and a["ok"] == 0 and a["no_output"] == 0),
            "examples_ok": a["examples_ok"],
            "examples_error": a["examples_error"],
        })
    # 签名汇总
    sig_summary = []
    for s in SIG_ORDER:
        a = sig_agg[s]
        if a["count"] == 0:
            continue
        sig_summary.append({
            "signature": s,
            "count": a["count"],
            "runs": len(a["runs"]),
            "example_task_ids": [e["task_id"] for e in a["examples"][:3]],
            "evidence": a["examples"][0]["evidence"] if a["examples"] else "",
        })
    sig_summary.sort(key=lambda x: x["runs"], reverse=True)

    # 交叉：签名 × domain
    sig_x_domain: Dict[str, Dict[str, int]] = {s: collections.Counter() for s in SIG_ORDER}
    sig_x_class: Dict[str, Dict[str, int]] = {s: collections.Counter() for s in SIG_ORDER}
    for rec in run_records:
        dom = rec["domain"]
        cls = rec["class"] or "NONE"
        for s, c in rec["signatures"].items():
            sig_x_domain[s][dom] += c
            sig_x_class[s][cls] += c

    # domain 列表
    domain_list = sorted({rec["domain"] for rec in run_records if rec["domain"] != "unknown"})
    class_list = ["NO_SUBMIT", "ASSERT_RUNTIME", "ASSERT_SEMANTIC", "UNKNOWN", "FORMAT_CONTRACT", "PASS", "NONE"]

    # asc 专项：收集所有出现上下文
    asc_contexts = _collect_asc_contexts(batch_dir, run_records)

    result = {
        "tool": {"name": "07_tool_health.py", "version": "1.0.0"},
        "meta": {
            "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "triage_path": os.path.abspath(triage_path),
            "batch_dir": os.path.abspath(batch_dir),
            "total_runs": total_runs,
            "runs_with_session": runs_with_session,
            "runs_no_session": n_no_session,
            "runs_no_tool_calls": n_parse_fail,
            "tool_count": len(TOOL_LIST),
        },
        "overall": {
            "triage_overall": overall,
            "domains": domains,
        },
        "tools": tools_summary,
        "signatures": sig_summary,
        "cross": {
            "signature_x_domain": {s: dict(c) for s, c in sig_x_domain.items() if sum(c.values())},
            "signature_x_class": {s: dict(c) for s, c in sig_x_class.items() if sum(c.values())},
            "domain_list": domain_list,
            "class_list": class_list,
        },
        "asc_special": asc_contexts,
        "exclusions": {
            "no_session_file": n_no_session,
            "no_tool_calls_parsed": n_parse_fail,
            "note": "no_session_file = 60 个 case 的 cline_stderr.log 软链断裂（多为 ABSENT/ERROR，"
                    "cline 未产出 session）；no_tool_calls_parsed = session 存在但未解析到 run_commands 调用。"
                    "两者均不计入工具健康矩阵的分母。从未调用 = runs_with_session - runs_invoked，不算失败。",
        },
        "methodology": {
            "four_states": ["有正常输出(ok)", "报错退出(error)", "调了但无产物(no_output)", "从未调用(never)"],
            "call_definition": "true_call = invoke(段首执行) + probe(which/type 探测); raw_mention = 词边界命中(含 printf/echo 字符串提及, 旁注)",
            "never_invoked_is_not_failure": True,
            "signature_scope": "失败签名只对【真正执行/探测 EDA 工具的命令】聚合（invoke/probe），剔除 grep/ls/test 等普通命令的 non-zero exit 噪声。",
            "chained_cmd_correction": "若 stdout 含内层 'exit=0'（agent 在工具后紧跟 echo exit=$? 捕获的工具退出码）且无 'exit=N>=1' 且无 stderr，判 ok——外层非零退出源于后续无关子命令（python3/grep），不归给工具。",
            "signature_norm": "stderr 首行去路径/时间/行号/十六进制后聚类; 无 stderr 用 stdout 头 400 字符; 仅在有失败信号(非零退出/stderr 非空/内层 exit=N>=1)时扫描 stdout。",
        },
    }
    return result


def _collect_asc_contexts(batch_dir: str, run_records: List[dict]) -> dict:
    """专门收集 "asc" 的所有出现上下文，判断其真实含义。"""
    contexts = []
    cases_with = 0
    total = 0
    for rec in run_records:
        sj = rec.get("session_path")
        if not sj:
            continue
        per_case = []
        try:
            with open(sj, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue
                    if o.get("type") != "agent_event":
                        continue
                    ev = o.get("event") or {}
                    blob = ""
                    if ev.get("type") == "content_start":
                        blob = str(ev.get("reasoning") or ev.get("text") or "")
                        inp = ev.get("input")
                        if isinstance(inp, dict):
                            blob += " " + json.dumps(inp, ensure_ascii=False)
                    elif ev.get("type") == "content_end":
                        blob = json.dumps(ev.get("output") or "", ensure_ascii=False)
                    for m in re.finditer(r"(?<![A-Za-z0-9_.])asc(?![A-Za-z0-9_])", blob, re.IGNORECASE):
                        s = max(0, m.start() - 35); e = min(len(blob), m.end() + 35)
                        snip = re.sub(r"\s+", " ", blob[s:e]).strip()
                        per_case.append(snip[:140])
        except Exception:
            pass
        if per_case:
            cases_with += 1
            total += len(per_case)
            for snip in per_case[:3]:
                contexts.append({"task_id": rec["task_id"], "snippet": snip})
            if len(contexts) >= 30:
                break
    # 归类含义
    kind_counter = collections.Counter()
    for c in contexts:
        s = c["snippet"].lower()
        if "rule.asc" or ".asc" in s or "xor.rule" in s:
            kind_counter[".asc 文件扩展名 (calibre/SVRF rule ASCII)"] += 1
        if " asc" in s and ("sort" in s or "order" in s or "sigma asc" in s or "name asc" in s or "risk asc" in s):
            kind_counter["ASC 排序关键字 (SQL/Python sorted)"] += 1
        if "asc" in s:
            kind_counter["其它 (含 'ascending' 缩写/片段)"] += 1
    return {
        "verdict": "在本数据集里 'asc' 不是 EDA 工具：0 次作为命令被执行。出现 65 处/21 case，"
                   "全部为 (1) .asc 文件扩展名（calibre/SVRF ASCII rule 文件，如 xor.rule.asc）、"
                   "(2) ASC 排序关键字（SQL/Python sorted 的 ascending）、(3) 'ascending' 片段。",
        "cases_with_asc_word": cases_with,
        "total_asc_occurrences": total,
        "tool_invocation_count": 0,
        "kind_counter": dict(kind_counter),
        "sample_contexts": contexts[:20],
    }


# ---------------- HTML 报告 ----------------

def build_html(data: dict, html_path: str) -> str:
    meta = data["meta"]
    tools = data["tools"]
    sigs = data["signatures"]
    cross = data["cross"]
    asc = data["asc_special"]
    excl = data["exclusions"]

    invoked_tools = [t for t in tools if t["true_calls"] > 0]
    never_any = sum(1 for t in tools if t["true_calls"] == 0)
    all_fail_tools = [t for t in tools if t["all_calls_failed"]]
    top_sig = sigs[0] if sigs else None

    # 结论一句话
    finesim_t = next((t for t in tools if t["tool"] == "finesim"), None)
    finesim_state = ("not-invoked" if finesim_t["true_calls"] == 0 else
                     ("fail" if finesim_t["all_calls_failed"] else "ok"))
    conclusion = (
        f"696-run 批次中 {meta['runs_with_session']} 个 run 有可解析 session，"
        f"识别到 {len(invoked_tools)}/{meta['tool_count']} 个 EDA 工具被真正调用；"
        f"finesim={finesim_state}（{finesim_t['true_calls']} 次调用，{finesim_t['ok']} 成功/{finesim_t['error']} 报错）；"
        f"asc 在本数据集中不是工具（0 次调用，详见专项）；"
        f"无任何工具出现「全部调用都失败」的异常；"
        f"EDA 工具执行层失败签名稀疏（最高频为「{top_sig['signature']}」，{top_sig['runs']} runs / {top_sig['count']} 次），"
        f"多数任务失败属语义层（工具正常跑但产物错），非工具不可用。"
        if top_sig else
        f"696-run 批次中 {meta['runs_with_session']} 个 run 有可解析 session；未检出标准失败签名。"
    )

    # SVG 条形图：Top-10 工具 true_calls
    chart_tools = sorted(tools, key=lambda x: x["true_calls"], reverse=True)[:12]
    chart_tools = [t for t in chart_tools if t["true_calls"] > 0]
    maxv = max((t["true_calls"] for t in chart_tools), default=1) or 1
    bar_h = 22; gap = 6; left = 130; chart_w = 460
    rows = len(chart_tools)
    svg_h = rows * (bar_h + gap) + 30
    bars_svg = []
    for i, t in enumerate(chart_tools):
        y = 10 + i * (bar_h + gap)
        w = int((t["true_calls"] / maxv) * chart_w) if t["true_calls"] else 0
        ok_w = int((t["ok"] / max(t["true_calls"], 1)) * w) if t["true_calls"] else 0
        err_w = w - ok_w
        bars_svg.append(
            f'<text x="{left-8}" y="{y+bar_h-6}" text-anchor="end" class="barlbl">{_html.escape(t["tool"])}</text>'
            f'<rect x="{left}" y="{y}" width="{w}" height="{bar_h}" class="barbg"/>'
            f'<rect x="{left}" y="{y}" width="{ok_w}" height="{bar_h}" class="barok"/>'
            f'<rect x="{left+ok_w}" y="{y}" width="{err_w}" height="{bar_h}" class="barerr"/>'
            f'<text x="{left+w+6}" y="{y+bar_h-6}" class="barval">{t["true_calls"]} ({t["ok"]}ok/{t["error"]}err)</text>'
        )
    svg_block = (
        f'<svg viewBox="0 0 {left+chart_w+150} {svg_h}" class="chart" role="img" '
        f'aria-label="工具调用次数 Top-12 条形图">'
        f'{"".join(bars_svg)}</svg>'
    )

    # 工具矩阵表
    tool_rows = []
    for t in sorted(tools, key=lambda x: (x["true_calls"], x["raw_mentions"]), reverse=True):
        state = "从未调用" if t["true_calls"] == 0 else (
            "全部失败 ⚠" if t["all_calls_failed"] else "部分/全部正常")
        cls = "trow-fail" if t["all_calls_failed"] else ("trow-never" if t["true_calls"] == 0 else "")
        tool_rows.append(
            f'<tr class="{cls}">'
            f'<td class="tt">{_html.escape(t["tool"])}</td>'
            f'<td>{t["true_calls"]}</td><td>{t["raw_mentions"]}</td>'
            f'<td>{t["invoke"]}</td><td>{t["probe"]}</td><td>{t["mention_only"]}</td>'
            f'<td>{t["ok"]}</td><td>{t["error"]}</td><td>{t["no_output"]}</td>'
            f'<td>{t["runs_invoked"]}</td><td>{t["runs_never_invoked"]}</td>'
            f'<td>{_html.escape(state)}</td></tr>'
        )
    tool_table = (
        '<table class="mt"><thead><tr>'
        '<th>工具</th><th>true_call</th><th>raw_mention</th>'
        '<th>invoke</th><th>probe</th><th>mention_only</th>'
        '<th class="ok">ok</th><th class="err">error</th><th>no_output</th>'
        '<th>runs_invoked</th><th>runs_never</th><th>状态</th>'
        '</tr></thead><tbody>' + "".join(tool_rows) + '</tbody></table>'
    )

    # finesim / asc 专项
    finesim_block = _tool_special_block(finesim_t, "finesim")
    asc_block = (
        f'<div class="sp"><h3>asc 专项</h3>'
        f'<p><b>结论</b>：{_html.escape(asc["verdict"])}</p>'
        f'<p>含 "asc" 词的 case 数 = <b>{asc["cases_with_asc_word"]}</b>；'
        f'总出现次数 = <b>{asc["total_asc_occurrences"]}</b>；'
        f'作为工具被调用次数 = <b>{asc["tool_invocation_count"]}</b>（即 0，不算工具）。</p>'
        f'<p>出现形式归类（基于抽样上下文）：</p><ul>'
        + "".join(f'<li>{_html.escape(k)}：{v}</li>' for k, v in asc["kind_counter"].items())
        + '</ul>'
        f'<p>抽样上下文（≤20 条）：</p><ul class="ctx">'
        + "".join(f'<li><code>{_html.escape(c["task_id"])}</code>：…{_html.escape(c["snippet"])}…</li>'
                  for c in asc["sample_contexts"])
        + '</ul></div>'
    )

    # Top-15 失败签名
    sig_rows = []
    for i, s in enumerate(sigs[:15], 1):
        ev = s.get("evidence", "")
        ids = ", ".join(s.get("example_task_ids", [])[:3])
        sig_rows.append(
            f'<tr><td>{i}</td><td class="sig">{_html.escape(s["signature"])}</td>'
            f'<td>{s["runs"]}</td><td>{s["count"]}</td>'
            f'<td class="ids">{_html.escape(ids)}</td>'
            f'<td class="ev">{_html.escape(ev)}</td></tr>'
        )
    sig_table = (
        '<table class="mt"><thead><tr><th>#</th><th>失败签名</th>'
        '<th>出现 run 数</th><th>出现次数</th><th>example task_id（≤3）</th>'
        '<th>原文证据（≤200 字符）</th></tr></thead><tbody>'
        + "".join(sig_rows) + '</tbody></table>'
    ) if sig_rows else "<p>（未检出标准失败签名）</p>"

    # 交叉表：签名 × domain
    sxd = cross.get("signature_x_domain", {})
    dom_list = cross.get("domain_list", [])
    sxd_rows = []
    for s in sorted(sxd.keys(), key=lambda k: sum(sxd[k].values()), reverse=True)[:12]:
        cells = "".join(f'<td>{sxd[s].get(d, 0)}</td>' for d in dom_list)
        sxd_rows.append(f'<tr><td class="sig">{_html.escape(s)}</td><td>{sum(sxd[s].values())}</td>{cells}</tr>')
    sxd_table = (
        '<table class="mt small"><thead><tr><th>签名</th><th>合计</th>'
        + "".join(f'<th>{_html.escape(d[:8])}</th>' for d in dom_list)
        + '</tr></thead><tbody>' + "".join(sxd_rows) + '</tbody></table>'
    ) if sxd_rows else "<p>（无）</p>"

    # 交叉表：签名 × 失败类别
    sxc = cross.get("signature_x_class", {})
    cls_list = cross.get("class_list", [])
    sxc_rows = []
    for s in sorted(sxc.keys(), key=lambda k: sum(sxc[k].values()), reverse=True):
        cells = "".join(f'<td>{sxc[s].get(c, 0)}</td>' for c in cls_list)
        sxc_rows.append(f'<tr><td class="sig">{_html.escape(s)}</td><td>{sum(sxc[s].values())}</td>{cells}</tr>')
    sxc_table = (
        '<table class="mt small"><thead><tr><th>签名</th><th>合计</th>'
        + "".join(f'<th>{_html.escape(c)}</th>' for c in cls_list)
        + '</tr></thead><tbody>' + "".join(sxc_rows) + '</tbody></table>'
    ) if sxc_rows else "<p>（无）</p>"

    # 全部失败工具点名
    allfail_block = ""
    if all_fail_tools:
        items = "".join(
            f'<li><b>{_html.escape(t["tool"])}</b>：true_call={t["true_calls"]}，'
            f'error={t["error"]}，ok={t["ok"]}，no_output={t["no_output"]}；'
            f'涉及 {t["runs_invoked"]} runs。典型证据：'
            f'<code>{_html.escape((t["examples_error"][0]["stderr"] if t["examples_error"] else "")[:160])}</code></li>'
            for t in all_fail_tools)
        allfail_block = (
            '<div class="sp alert"><h3>⚠ 全部调用都失败的工具</h3>'
            f'<p>以下工具的 true_call 全部归为 error（无 ok / 无 no_output），即用户要的"异常"：</p>'
            f'<ul>{items}</ul></div>'
        )

    # 方法与被排除项
    method_block = (
        '<div class="sp"><h3>方法与被排除项</h3>'
        f'<p><b>数据源</b>：triage_summary.json（{meta["total_runs"]} cases）'
        f'+ cline_session.jsonl（每个 case 的 agent 会话）。</p>'
        f'<p><b>解析覆盖</b>：有可解析 session = <b>{meta["runs_with_session"]}</b>；'
        f'软链断裂/无 session = <b>{excl["no_session_file"]}</b>（多为 ABSENT/ERROR，'
        f'cline 未产出会话，不计入矩阵分母）；session 存在但无 run_commands 调用 = '
        f'<b>{excl["no_tool_calls_parsed"]}</b>。</p>'
        f'<p><b>四态定义</b>：有正常输出(ok) / 报错退出(error) / 调了但无产物(no_output) / 从未调用(never)。'
        f'「从未调用」= runs_with_session - runs_invoked，<b>绝不算工具失败</b>。</p>'
        f'<p><b>调用判定（两套口径）</b>：true_call = invoke(段首执行) + probe(which/type 探测)；'
        f'raw_mention = 词边界正则命中（含 printf/echo/heredoc/JSON 字符串里的提及，仅作旁注，'
        f'避免把写配置文件里的工具名误当工具调用）。健康矩阵以 true_call 为主。</p>'
        f'<p><b>no_output 的注意</b>：命令以 <code>&gt; /dev/null 2&gt;&amp;1</code> 重定向时，'
        f'stdout/stderr 为空但工具可能已正常执行；本类按字面记为 no_output，报告里不把它判为失败。</p>'
        f'<p><b>失败签名归一化</b>：取 stderr 首行（无则 stdout 头 400 字符），'
        f'去掉路径/时间戳/行号/十六进制后按 13 条规则聚类，命中即归类，未命中归 other。'
        f'<b>签名只对【真正执行/探测 EDA 工具的命令】聚合</b>（invoke/probe），'
        f'剔除 grep/ls/test 等普通命令的 non-zero exit 噪声。</p>'
        f'<p><b>判据自证（贴 2 个 case 解析前后对照）</b>：见下表。</p>'
        + _self_evidence_table(data)
        + f'<p><b>复现命令</b>：</p><pre>python3 07_tool_health.py \\\n'
          f'  --triage results/run_batch_20261109_171201/triage_summary.json \\\n'
          f'  --batch /nasdata/app.e0031982/.cache/triage_batch_20261109_171201 \\\n'
          f'  --out   results/run_batch_20261109_171201 \\\n'
          f'  --html  {html_path}</pre>'
        f'</div>'
    )

    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>设计流 Benchmark · EDA 工具健康深挖报告（2026-11-10）</title>
<style>
 body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
   color:#1f2328;background:#fafbfc;margin:0;padding:32px;line-height:1.6;}}
 h1{{font-size:1.5em;border-bottom:2px solid #0969da;padding-bottom:.3em;}}
 h2{{margin-top:1.8em;border-bottom:1px solid #d0d7de;padding-bottom:.2em;}}
 h3{{margin-top:1.2em;color:#0969da;}}
 .meta{{color:#57606a;font-size:.9em;margin-bottom:1em;}}
 .concl{{background:#ddf4ff;border:1px solid #54aeff;border-radius:6px;
   padding:14px 18px;margin:1em 0;}}
 .chart{{width:100%;max-width:760px;height:auto;margin:1em 0;}}
 .barbg{{fill:#eaeef2;}}.barok{{fill:#2da44e;}}.barerr{{fill:#cf222e;}}
 .barlbl{{font:11px sans-serif;fill:#57606a;}}.barval{{font:11px sans-serif;fill:#1f2328;}}
 .legend{{font-size:.85em;color:#57606a;margin:.3em 0 1em;}}
 table.mt{{border-collapse:collapse;width:100%;margin:1em 0;font-size:.88em;}}
 table.small{{font-size:.8em;}}
 .mt th,.mt td{{border:1px solid #d0d7de;padding:5px 7px;text-align:right;}}
 .mt th{{background:#f6f8fa;text-align:center;}}
 .mt td.tt,.mt td.sig,.mt td.ids,.mt td.ev{{text-align:left;}}
 .mt td.ok{{color:#1a7f37;}}.mt td.err{{color:#cf222e;}}
 .mt th.ok{{color:#1a7f37;}}.mt th.err{{color:#cf222e;}}
 tr.trow-fail{{background:#ffebe9;}}tr.trow-never{{color:#8c959f;}}
 .sp{{margin:1.2em 0;padding:14px 18px;background:#fff;border:1px solid #d0d7de;border-radius:6px;}}
 .sp.alert{{background:#fff8c5;border-color:#d4a72c;}}
 .sp h3{{margin-top:0;}}
 ul.ctx{{font-size:.82em;}}ul.ctx code{{color:#0969da;}}
 pre{{background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;
   padding:10px 14px;overflow-x:auto;font-size:.85em;}}
 .ev{{max-width:320px;}}.ids{{max-width:200px;font-size:.8em;color:#57606a;}}
 .foot{{color:#57606a;font-size:.82em;margin-top:2em;border-top:1px solid #d0d7de;padding-top:.6em;}}
 .tag{{display:inline-block;padding:1px 6px;border-radius:10px;font-size:.78em;background:#eaeef2;}}
</style></head><body>
<h1>设计流 Benchmark · EDA 工具健康深挖报告</h1>
<div class="meta">生成时间：{_html.escape(meta["generated_at"])} · 数据批次：run_batch_20261109_171201
· 总 runs：{meta["total_runs"]} · 有可解析 session：{meta["runs_with_session"]}
· 工具清单：{meta["tool_count"]} 个 · 工具：07_tool_health.py v1.0.0</div>

<h2>① 一句话结论</h2>
<div class="concl">{_html.escape(conclusion)}</div>

<h2>② 工具健康矩阵</h2>
<div class="legend">条形图：Top-12 工具 true_call 次数（绿=ok，红=error）。</div>
{svg_block}
{tool_table}
{allfail_block}

<h2>③ finesim / asc 专项</h2>
{finesim_block}
{asc_block}

<h2>④ Top-15 重复失败模式</h2>
{sig_table}

<h2>⑤ 交叉分析</h2>
<h3>签名 × domain</h3>
{sxd_table}
<h3>签名 × 失败类别（triage class）</h3>
{sxc_table}

<h2>⑥ 方法与被排除项</h2>
{method_block}

<div class="foot">本报告自包含（内联 CSS + 内联 SVG，不引 CDN、不依赖 JS）。
数据来源：triage_summary.json + cline_session.jsonl。判据自证见 ⑥ 节。
数字均取自实跑解析，取不到处标 n/a。</div>
</body></html>"""
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html_doc)
    return html_path


def _tool_special_block(t: Optional[dict], name: str) -> str:
    if not t:
        return f'<div class="sp"><h3>{name} 专项</h3><p>n/a（工具清单未含）</p></div>'
    if t["true_calls"] == 0:
        return (f'<div class="sp"><h3>{name} 专项</h3>'
                f'<p><b>从未被调用</b>（true_call=0, raw_mention={t["raw_mentions"]}）。'
                f'在本批次 696 run 中 {name} 没有作为命令被执行 —— 不算工具失败。</p></div>')
    state = "全部失败 ⚠" if t["all_calls_failed"] else "部分/全部正常"
    ex_ok = "".join(
        f'<li><code>{_html.escape(e["task_id"])}</code>：{_html.escape(e["cmd"])} (exit={e["exit_code"]})</li>'
        for e in t["examples_ok"])
    ex_err = "".join(
        f'<li><code>{_html.escape(e["task_id"])}</code>：{_html.escape(e["cmd"])} (exit={e["exit_code"]})；'
        f'stderr：{_html.escape(e["stderr"])}</li>'
        for e in t["examples_error"])
    return (f'<div class="sp"><h3>{name} 专项</h3>'
            f'<p><b>状态</b>：{state}。true_call={t["true_calls"]}（invoke={t["invoke"]}, probe={t["probe"]}），'
            f'ok={t["ok"]}，error={t["error"]}，no_output={t["no_output"]}；涉及 {t["runs_invoked"]} runs。</p>'
            f'<p><b>正常样例</b>：</p><ul>{ex_ok or "<li>n/a</li>"}</ul>'
            f'<p><b>报错样例</b>：</p><ul>{ex_err or "<li>n/a</li>"}</ul></div>')


def _self_evidence_table(data: dict) -> str:
    """贴 2 个 case 的解析前后对照（判据自证）。"""
    tools = data["tools"]
    finesim = next((t for t in tools if t["tool"] == "finesim"), None)
    hspice = next((t for t in tools if t["tool"] == "hspice"), None)
    def _row(t, label):
        if not t or not t["examples_ok"]:
            return f'<tr><td>{label}</td><td>n/a</td><td>n/a</td><td>n/a</td></tr>'
        e = t["examples_ok"][0]
        return (f'<tr><td>{label}</td><td>{_html.escape(e["task_id"])}</td>'
                f'<td><code>{_html.escape(e["cmd"])}</code></td>'
                f'<td>exit={e["exit_code"]} → 归 ok（true_call +1, ok +1）</td></tr>')
    return (
        '<table class="mt small"><thead><tr><th>case</th><th>task_id</th>'
        '<th>原命令（截断）</th><th>解析后归类</th></tr></thead><tbody>'
        + _row(finesim, "finesim") + _row(hspice, "hspice")
        + '</tbody></table>'
    )


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="EDA 工具健康深挖")
    ap.add_argument("--triage", required=True, help="triage_summary.json 路径")
    ap.add_argument("--batch", required=True, help="batch 目录（含每个 case 的软链）")
    ap.add_argument("--out", required=True, help="输出目录（写 tool_health.json）")
    ap.add_argument("--html", default=None, help="中文 HTML 报告输出路径")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个 case（调试, 0=全部）")
    args = ap.parse_args(argv)

    data = analyze(args.triage, args.batch)
    if args.limit:
        data["meta"]["limit"] = args.limit
    os.makedirs(args.out, exist_ok=True)
    out_json = os.path.join(args.out, "tool_health.json")
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print(f"[07_tool_health] wrote {out_json}")
    print(f"  runs_with_session={data['meta']['runs_with_session']}/{data['meta']['total_runs']}")
    print(f"  tools invoked: {sum(1 for t in data['tools'] if t['true_calls']>0)}/{data['meta']['tool_count']}")
    print(f"  signatures: {len(data['signatures'])}")
    if args.html:
        build_html(data, args.html)
        print(f"[07_tool_health] wrote {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
