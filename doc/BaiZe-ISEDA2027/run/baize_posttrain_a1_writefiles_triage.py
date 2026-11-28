#!/usr/bin/env python3
"""Triage A1 (Qwen3.5-2B) run1 write_files / tool-rejection traces."""
import json, os, re
from collections import Counter, defaultdict

RUN1 = "/nas_data/app.e0031982/posttrain_5run_eval/A1_qwen35_2b/run1"
CODEGEN = os.path.join(RUN1, "codegen.log")
JSONL = os.path.join(RUN1, "completed_code_generation.jsonl")
REPORT = os.path.join(RUN1, "final_report.json")
A0_PERTASK = "/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baseline_A0_base_ragfix_run1_pertask.json"

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
def clean(s): return ANSI_RE.sub("", s)

with open(CODEGEN, "r", encoding="utf-8", errors="replace") as f:
    raw_lines = f.readlines()
lines = [clean(l).rstrip("\n") for l in raw_lines]

tool_call_re = re.compile(r"^\[([a-z_]+)\]\s")
unavail_re = re.compile(r"unavailable tool '([^']+)'")
access_restricted_re = re.compile(r"ACCESS RESTRICTED")
editor_err_re = re.compile(r"Invalid input.*new_text|expected string, received undefined", re.I)

tool_calls = Counter()
reject_tool = Counter()
reject_reason = Counter()
editor_errors = 0
run_commands_blocked = 0

for ln in lines:
    m = tool_call_re.match(ln)
    if m:
        tool_calls[m.group(1)] += 1
    if "rejected before execution" in ln or "AI_NoSuchToolError" in ln:
        um = unavail_re.search(ln)
        if um:
            reject_tool[um.group(1)] += 1
            reject_reason["unavailable-tool"] += 1
    if access_restricted_re.search(ln):
        run_commands_blocked += 1
    if editor_err_re.search(ln):
        editor_errors += 1

per_task = {}
with open(JSONL, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        d = json.loads(line)
        tid = d.get("task_id")
        comp = d.get("completion", "") or ""
        status = d.get("status", "")
        looks_like_code = ("\n" in comp) or comp.strip().startswith(("def ", "import ", "from ", "class "))
        per_task[tid] = {"task_id": tid, "status": status,
                         "has_code": bool(status == "success" and looks_like_code),
                         "completion_chars": len(comp)}

fr = json.load(open(REPORT, "r", encoding="utf-8"))
for tid, info in fr.get("details_per_task", {}).items():
    if tid in per_task:
        per_task[tid]["pass_rate"] = info.get("pass_rate")
        per_task[tid]["generation_statuses"] = info.get("generation_statuses", [])
        per_task[tid]["execution_statuses"] = info.get("execution_statuses", [])
        per_task[tid]["error_types"] = info.get("error_types", [])

task_start_re = re.compile(r"\[worker-\d+\] (?:开始任务|任务) (EDA-Eval-PyAether-\d+)")
cur = None
per_task_tools = defaultdict(Counter)
per_task_reject = defaultdict(Counter)
for ln in lines:
    m = task_start_re.search(ln)
    if m and "开始任务" in ln:
        cur = m.group(1)
    if cur:
        tm = tool_call_re.match(ln)
        if tm: per_task_tools[cur][tm.group(1)] += 1
        if "rejected before execution" in ln or "AI_NoSuchToolError" in ln:
            um = unavail_re.search(ln)
            if um: per_task_reject[cur][um.group(1)] += 1

classified = []
for tid, d in per_task.items():
    tools = per_task_tools.get(tid, Counter())
    rej = per_task_reject.get(tid, Counter())
    mcp_rej = rej.get("search_apis",0)+rej.get("get_api_details",0)+rej.get("search_apis_by_keyword",0)+rej.get("write_files",0)
    editor_used = tools.get("editor",0)
    submit_used = tools.get("submit_and_exit",0)
    if d["has_code"]:
        cls = "c_capability" if (d.get("pass_rate")==0) else "pass"
    else:
        if mcp_rej > 0 and editor_used == 0: cls = "a_protocol_incompat_mcp"
        elif rej.get("write_files",0) > 0 and editor_used == 0: cls = "a_protocol_incompat_writefiles"
        elif editor_used > 0: cls = "b_path_or_schema"
        elif submit_used > 0: cls = "d_submit_text_only"
        else: cls = "a_protocol_incompat_mcp" if mcp_rej > 0 else "other"
    classified.append({"task_id": tid, "has_code": d["has_code"], "pass_rate": d.get("pass_rate"),
                       "gen_status": d.get("generation_statuses"), "error_types": d.get("error_types"),
                       "editor_calls": editor_used, "search_apis_calls": tools.get("search_apis",0),
                       "get_api_details_calls": tools.get("get_api_details",0),
                       "write_files_calls": tools.get("write_files",0), "submit_calls": submit_used,
                       "mcp_rejections": dict(rej) if rej else {}, "class": cls})
cls_counts = Counter(c["class"] for c in classified)

snippets = []
def extract_snippet(label, pat):
    for i, ln in enumerate(lines):
        if pat in ln:
            start = max(0, i-1); end = min(len(lines), i+6)
            return {"label": label, "start_line": start+1, "lines": lines[start:end]}
    return None
snippets.append(extract_snippet("search_apis rejected", "Tool call search_apis was rejected"))
snippets.append(extract_snippet("write_files rejected", "Tool call write_files was rejected"))
snippets.append(extract_snippet("run_commands hook-blocked", "ACCESS RESTRICTED: outside the sandbox workspace"))
snippets.append(extract_snippet("editor schema error", "Invalid input: expected string, received undefined"))
snippets.append(extract_snippet("model gives up -> submit", "Submission recorded"))
snippets = [s for s in snippets if s]

a0 = json.load(open(A0_PERTASK, "r", encoding="utf-8"))
a0_tools = a0.get("aggregate_tool_calls", {})
a0_reject = a0.get("aggregate_reject_reasons", {})
a0_metrics = a0.get("four_metric_means_over_tasks", {})

fairness = {
  "A0_base_ragfix_run1": {"model":"MiniCPM5-2B","endpoint":":8098","eval_dir":a0.get("eval_dir"),
    "aggregate_tool_calls":a0_tools,"aggregate_reject_reasons":a0_reject,
    "rag_queried_rate":a0_metrics.get("rag_queried_rate"),
    "tool_call_count_mean":a0_metrics.get("tool_call_count_mean"),
    "cline_mcp_settings_present":True},
  "A1_qwen35_2b_run1": {"model":"Qwen3.5-2B","endpoint":":8097",
    "aggregate_tool_calls":dict(tool_calls),
    "aggregate_reject_reasons":{"unavailable-tool":int(sum(reject_tool.values())),"by_tool":dict(reject_tool)},
    "run_commands_hook_blocked":run_commands_blocked,"editor_schema_errors":editor_errors,
    "rag_queried_rate":0.0,"cline_mcp_settings_present":False},
  "same_caliber_check": {
    "prompt_template":"eval_sys_prompt_template_no_sandbox.md (both)",
    "harness":"run_cline_script.sh -p 8 -n (both)",
    "hook":"PreToolUse sandbox hook (both)",
    "benchmark":"EDA-Eval-PyAether 158 (both)",
    "toolset_A0":"core + MCP(pyAether_MCP_server: search_apis/get_api_details/search_apis_by_keyword/run_code)",
    "toolset_A1":"core only (MCP MISSING: cline_mcp_settings.json wiped)",
    "verdict":"CALIBER MISMATCH (infra regression, not model): A1 lost MCP tools because ~/.cline/data/settings/cline_mcp_settings.json was wiped by 2026-11-28 HOME snapshot rollback (wake870). A0 (Nov 24) had the file -> MCP callable -> 45.06%. Single-variable design broken by missing MCP config, NOT by base-model capability."},
}

out = {
  "generated_for":"A1_qwen35_2b run1 (2026-11-28 18:34 batch)",
  "summary":{"total_tasks":len(per_task),
    "has_code":sum(1 for c in classified if c["has_code"]),
    "no_code":sum(1 for c in classified if not c["has_code"]),
    "pass_count":sum(1 for c in classified if c.get("pass_rate")==1.0),
    "pass_rate":fr.get("metrics",{}).get("pass_rate")},
  "aggregate_tool_calls":dict(tool_calls),
  "aggregate_rejected_tools":dict(reject_tool),
  "aggregate_reject_reasons":dict(reject_reason),
  "run_commands_hook_blocked":run_commands_blocked,
  "editor_schema_errors":editor_errors,
  "class_counts":dict(cls_counts),
  "class_legend":{"a_protocol_incompat_mcp":"no code; MCP tools rejected as unavailable; never reached editor",
    "a_protocol_incompat_writefiles":"no code; write_files rejected as unavailable; never reached editor",
    "b_path_or_schema":"editor used but no code landed (path/schema)",
    "d_submit_text_only":"submit_and_exit text, no editor code",
    "c_capability":"code emitted but failed (logic/API misuse) -- genuine gap",
    "pass":"passed","other":"uncategorized"},
  "per_task":classified,
  "raw_trace_snippets":snippets,
  "fairness_A0_vs_A1":fairness,
  "root_cause":"A1 run1 1.27% is dominated by an INFRA/PROTOCOL regression, not by Qwen3.5-2B capability: cline MCP settings (~/.cline/data/settings/cline_mcp_settings.json) was wiped by 2026-11-28 HOME snapshot rollback (wake870). run_cli.sh:109 copies it per-worker with `cp ... || true`, so silent skip left A1 workers with NO pyAether_MCP_server -> search_apis/get_api_details/run_code all rejected as unavailable (131 search_apis + 12 get_api_details + 10 search_apis_by_keyword + 4 write_files). no_sandbox.md prompt instructs model to use search_apis/get_api_details, so Qwen3.5-2B followed the prompt calling a non-existent tool. A0 (Nov 24, pre-wipe) had the file -> MCP callable (1044 search_apis/663 get_api_details/179 run_code, rag_queried_rate=0.9937) -> 45.06%. Fix = restore cline_mcp_settings.json then re-run A1.",
}

outpath_json = os.path.join(RUN1, "write_files_triage.json")
outpath_md = os.path.join(RUN1, "write_files_triage.md")
with open(outpath_json, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

md = []
md.append("# A1 (Qwen3.5-2B) run1 — write_files / tool-rejection triage\n")
md.append("> 数据源: codegen.log + completed_code_generation.jsonl + final_report.json + A0_base_ragfix_run1_pertask.json\n")
md.append("## 1. 结论（首屏）\n")
md.append("- **A1 run1 = 1.27% (2/158) 主因 = INFRA/协议回归，不是 Qwen3.5-2B 能力不行。**\n")
md.append("- cline MCP 配置 `~/.cline/data/settings/cline_mcp_settings.json` 在 2026-11-28 HOME snapshot 回退(wake870)中被清空。`run_cli.sh:109` 用 `cp ... || true` 静默跳过 ⇒ A1 8 worker 均无 `pyAether_MCP_server` ⇒ `search_apis/get_api_details/run_code` 全判 unavailable。\n")
md.append(f"- `no_sandbox.md` prompt 明文要求用 `search_apis/get_api_details`，Qwen3.5-2B 照做 → 共 {int(sum(reject_tool.values()))} 次 unavailable-tool 拒绝(search_apis {reject_tool.get('search_apis',0)}/get_api_details {reject_tool.get('get_api_details',0)}/search_apis_by_keyword {reject_tool.get('search_apis_by_keyword',0)}/write_files {reject_tool.get('write_files',0)}) → 无码 → 1.27%。\n")
md.append("- **公平性**: A0_base_ragfix(11-24,wipe 前)同 prompt/同 harness/同 hook 但 MCP 文件在位 → search_apis 1044/get_api_details 663/run_code 179 成功, rag_queried_rate=0.9937 → 45.06%。**两臂工具集不同 ⇒ 口径不一致 ⇒ 不可直接配对。**\n")
md.append("- **裁决: 属「协议适配问题」→ 修**(用户令 22:3x 第3条)。恢复 cline_mcp_settings.json → 重跑 A1 run1 冒烟确认 MCP 可用 + 命中率回升 → A0 1-run 校准 → A1 run1-5。\n")
md.append("\n## 2. 汇总统计\n")
md.append(f"- 总任务 {out['summary']['total_tasks']}；有码 {out['summary']['has_code']}；无码 {out['summary']['no_code']}；PASS {out['summary']['pass_count']}；Pass@1 {out['summary']['pass_rate']:.4f}\n")
md.append(f"- run_commands 被 hook 阻断: {run_commands_blocked}；editor schema 错误: {editor_errors}\n")
md.append("\n### 2.1 工具调用 (aggregate exact)\n")
md.append("| 工具 | 次数 |\n|---|---:|\n")
for t,c in sorted(tool_calls.items(), key=lambda x:-x[1]):
    md.append(f"| `{t}` | {c} |\n")
md.append("\n### 2.2 被拒工具 (unavailable-tool exact)\n")
md.append("| 工具 | 拒绝次数 |\n|---|---:|\n")
for t,c in sorted(reject_tool.items(), key=lambda x:-x[1]):
    md.append(f"| `{t}` | {c} |\n")
md.append("\n## 3. 三堆分类 (per-task boundary 近似, aggregate 精确)\n")
md.append("| 分类 | 计数 | 含义 |\n|---|---:|---|\n")
for k,v in sorted(cls_counts.items(), key=lambda x:-x[1]):
    md.append(f"| {k} | {v} | {out['class_legend'].get(k,'')} |\n")
md.append("\n## 4. 公平性对照 (A0 vs A1)\n")
md.append("| 项 | A0_base_ragfix(11-24) | A1_qwen35_2b(11-28) | 同? |\n|---|---|---|---|\n")
md.append("| 模型 | MiniCPM5-2B | Qwen3.5-2B | **唯一应变量** |\n")
md.append("| endpoint | :8098 | :8097 | - |\n")
md.append("| prompt | no_sandbox.md | no_sandbox.md | 同 |\n")
md.append("| harness | run_cline_script -p8 -n | run_cline_script -p8 -n | 同 |\n")
md.append("| hook | PreToolUse sandbox | PreToolUse sandbox | 同 |\n")
md.append("| benchmark | 158 题 | 158 题 | 同 |\n")
md.append("| MCP 配置文件 | 在位 | **被 wipe(缺失)** | 不同 |\n")
md.append("| 可用工具集 | core+MCP | 仅 core(4) | 不同 |\n")
md.append(f"| search_apis 成功 | {a0_tools.get('search_apis',0)} | 0 | 不同 |\n")
md.append(f"| get_api_details 成功 | {a0_tools.get('get_api_details',0)} | 0 | 不同 |\n")
md.append(f"| run_code 成功 | {a0_tools.get('run_code',0)} | 0 | 不同 |\n")
md.append(f"| rag_queried_rate | {a0_metrics.get('rag_queried_rate')} | 0.0 | 不同 |\n")
md.append("| Pass@1 | 45.06%(5-run) | 1.27%(run1) | 不可比 |\n")
md.append(f"\n**裁决**: {fairness['same_caliber_check']['verdict']}\n")
md.append("\n## 5. 原始 trace 片段\n")
for s in snippets:
    md.append(f"### {s['label']} (codegen.log L{s['start_line']}+)\n")
    md.append("```\n")
    for ln in s["lines"]:
        md.append(ln[:500]+"\n")
    md.append("```\n")
md.append("\n## 6. 修法(最小)\n")
md.append("1. 恢复 `~/.cline/data/settings/cline_mcp_settings.json`(见下)指向在跑 eda-mcp :18888 SSE。\n")
md.append("2. 重跑 A1 run1 冒烟(-p8 -n)，确认 search_apis/get_api_details 不再被拒、命中率回升。\n")
md.append("3. A0 1-run 校准(重启 base:8098+重装 minicpm5 parser)，确认 45.06% 量级不掉。\n")
md.append("4. A1 run1-5 → 5-run summary → A0_vs_A1 配对(McNemar/bootstrap)。\n")
md.append("\n```json\n")
md.append(json.dumps({"mcpServers":{"pyAether_MCP_server":{"url":"http://127.0.0.1:18888/sse","type":"sse","disabled":False,"autoApprove":["search_apis","get_api_details","search_apis_by_keyword","run_code"]}}}, ensure_ascii=False, indent=2))
md.append("\n```\n")
md.append("\n## 7. 证据索引\n")
md.append(f"- A1 run1 codegen.log: `{CODEGEN}`\n")
md.append(f"- A1 run1 final_report.json: `{REPORT}`\n")
md.append(f"- A0 pertask: `{A0_PERTASK}`\n")
md.append("- run_cli.sh:109 (MCP cp): /nas_data/app.e0031982/code/eda_fastmcp/scripts/run_cli.sh\n")
md.append(f"- 本 triage: `{outpath_json}` / `{outpath_md}`\n")

with open(outpath_md, "w", encoding="utf-8") as f:
    f.write("".join(md))

print("WROTE", outpath_json)
print("WROTE", outpath_md)
print("summary:", out["summary"])
print("class_counts:", dict(cls_counts))
print("rejected_tools:", dict(reject_tool))
print("tool_calls:", dict(tool_calls))
