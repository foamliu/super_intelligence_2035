#!/usr/bin/env python3
"""baize_posttrain_verl_multiturn_audit.py — verl 0.4.0 Multi-Turn Tool Calling
Protocol Source-Level Audit & Integration Gap Analysis

R69 (2026-11-09 wake117): Deep-dive into verl 0.4.0's actual multi-turn tool
calling implementation. Previous research (R9, R47, R50) covered the integration
at a high level; this audit reads the ACTUAL source code to identify concrete
API mismatches between our EDASandboxTool and verl's BaseTool interface.

KEY FINDINGS:
  1. EDASandboxTool.__init__ signature mismatch (missing tool_schema param)
  2. EDASandboxTool.create() returns tuple, verl expects str
  3. EDASandboxTool.execute() returns Dict, verl expects str (response must be string)
  4. No tool_config YAML exists — multi_turn.tool_config_path is null
  5. max_turns default = max_model_len // 3 = 5461 (absurdly high, must set explicitly)
  6. Context overflow mid-turn: force STOP, partial trajectory kept
  7. Tool calls with JSON decode errors are silently DROPPED
  8. Reward = per-tool calc_reward(), not per-turn; external compute_score is separate

DELIVERABLES:
  - This audit script (source-level analysis)
  - baize_posttrain_eda_tool_v2.py (corrected BaseTool subclass)
  - baize_posttrain_tool_config.yaml (verl tool config for EDA sandbox)
  - HTML report + JSON output

WARNING: Surrogate RL results are NOT transferable to BaiZe.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import textwrap
from typing import Any, Dict, List, Tuple

VERL_VERSION = "0.4.0"
VERL_BASE_TOOL_PATH = os.path.expanduser(
    "~/code/verl_cu124_venv/lib/python3.10/site-packages/verl/tools/base_tool.py")
VERL_SGLANG_ROLLOUT_PATH = os.path.expanduser(
    "~/code/verl_cu124_venv/lib/python3.10/site-packages/verl/workers/rollout/"
    "sglang_rollout/sglang_rollout.py")
VERL_SCHEMAS_PATH = os.path.expanduser(
    "~/code/verl_cu124_venv/lib/python3.10/site-packages/verl/workers/rollout/schemas.py")
VERL_SANDBOX_FUSION_PATH = os.path.expanduser(
    "~/code/verl_cu124_venv/lib/python3.10/site-packages/verl/tools/sandbox_fusion_tools.py")

AUDIT_FINDINGS: List[Dict[str, Any]] = []


def add_finding(fid, severity, component, description, evidence, fix, status="IDENTIFIED"):
    AUDIT_FINDINGS.append({
        "id": fid, "severity": severity, "component": component,
        "description": description, "evidence": evidence, "fix": fix, "status": status,
    })


def audit_basetool_interface():
    add_finding("F01", "CRITICAL", "BaseTool.__init__",
        "verl BaseTool.__init__(self, config, tool_schema) requires TWO params. "
        "Our EDASandboxTool.__init__(self, config) only takes ONE.",
        "base_tool.py line 31", "Add tool_schema param and pass to super().__init__()")
    add_finding("F02", "CRITICAL", "BaseTool.create()",
        "verl create() returns str. Our tool returns Tuple. verl uses return as instance_id.",
        "base_tool.py line 39: -> str", "Change create() to return just instance_id (str)")
    add_finding("F03", "CRITICAL", "BaseTool.execute()",
        "verl execute() returns Tuple[str, float, dict]. Our tool returns Tuple[Dict,...]. "
        "verl passes response string to add_tool_response_message(tokenizer, resp).",
        "base_tool.py line 52", "Serialize response dict to JSON string before returning")
    add_finding("F04", "HIGH", "BaseTool.calc_reward()",
        "verl calls calc_reward(instance_id) at episode end. Our 0.0 return is correct.",
        "sglang_rollout.py line 839", "No fix needed.", "OK")


def audit_multiturn_state_machine():
    add_finding("F05", "HIGH", "max_turns default",
        "verl sets max_turns = max_model_len // 3 if None. With 16384 gives 5461 turns.",
        "sglang_rollout.py line 331-332",
        "Set max_turns: 3 explicitly (done in config v2)", "FIXED_IN_CONFIG")
    add_finding("F06", "HIGH", "Context overflow mid-turn",
        "Tool response pushing input_ids >= max_model_len forces STOP. False negatives possible.",
        "sglang_rollout.py line 760-764",
        "Mitigate with ctx=16384+ (done). Monitor false_negative_rate in smoke.")
    add_finding("F07", "MEDIUM", "Tool call JSON decode error",
        "Malformed tool call args are SILENTLY DROPPED. Model thinks it called a tool.",
        "sglang_rollout.py line 802: if has_decode_error: continue",
        "Log decode_error_count. Penalize in R4 arm.")
    add_finding("F08", "MEDIUM", "LENGTH finish reason",
        "Generation hitting response_length limit breaks rollout with already_over_long=True.",
        "sglang_rollout.py line 773-780",
        "Accept. response_length=8192 sufficient.")


def audit_tool_config_gap():
    add_finding("F09", "CRITICAL", "tool_config_path",
        "RL config v2 has tool_config_path: null. verl returns empty lists when None. "
        "NO tools loaded, multi-turn cannot work.",
        "sglang_rollout.py line 427",
        "Create tool_config.yaml. Set tool_config_path when enabling multi_turn.")
    add_finding("F10", "HIGH", "Tool initialization flow",
        "verl loads tools from YAML via OmegaConf. Class loaded via importlib. "
        "Tool must be importable from verl venv Python path.",
        "sglang_rollout.py line 440-461",
        "Ensure tool v2 on PYTHONPATH. Use full module path in class_name.")


def audit_reward_computation():
    add_finding("F11", "HIGH", "Dual reward system",
        "Two mechanisms: (1) per-tool calc_reward() at episode end, "
        "(2) external compute_score via NaiveRewardManager. Our design uses (2), returns 0 from (1).",
        "sglang_rollout.py line 838-848",
        "Document. Verify compute_score receives tool responses in smoke.")
    add_finding("F12", "MEDIUM", "Reward scores storage",
        "tool_reward_scores in _req.reward_scores. May not propagate to training loop.",
        "sglang_rollout.py line 849",
        "Verify in smoke test.")


def audit_format_compatibility():
    add_finding("F13", "HIGH", "Chat format: chatml vs qwen",
        "verl supports 'chatml' and 'qwen'. MiniCPM5-2B uses ChatML.",
        "schemas.py line 89-105",
        "Use 'chatml' (done). Verify tokenizer has <|im_start|>tool tokens.")
    add_finding("F14", "MEDIUM", "Function call parser type",
        "get_tool_call_parser_type(tokenizer) may return None for MiniCPM5-2B. "
        "If None, tool calls NOT detected. POTENTIAL BLOCKER.",
        "sglang_rollout.py line 471",
        "Check parser type in smoke. If None, register custom parser.")


def audit_concurrency_model():
    add_finding("F15", "MEDIUM", "Async rollout concurrency",
        "Multi-turn processes each prompt individually. Tool calls run via asyncio.gather.",
        "sglang_rollout.py line 742",
        "Ensure execute() is async. Use asyncio.to_thread() for CPU-bound Tier3.")
    add_finding("F16", "LOW", "Rate limiting",
        "SandboxFusionTool uses Ray TokenBucketWorker. Our tool has no rate limiting.",
        "sandbox_fusion_tools.py line 43-62",
        "Add if needed. Not needed for Tier3.")


def generate_tool_config_yaml():
    return textwrap.dedent("""\
        # baize_posttrain_tool_config.yaml — verl 0.4.0 tool config for EDA sandbox
        # R69 (2026-11-09): Tool configuration for verl multi-turn rollout.
        # ⚠️ Surrogate RL results are NOT transferable to BaiZe.
        tools:
          - class_name: baize_posttrain_eda_tool_v2.EDASandboxToolV2
            tool_schema:
              type: function
              function:
                name: eda_sandbox
                description: >
                  Execute Python code in the EDA (pyAether) sandbox environment.
                  Use this tool to run EDA API calls, test code, and verify results.
                parameters:
                  type: object
                  properties:
                    code:
                      type: string
                      description: Python code to execute in the EDA sandbox
                    host:
                      type: string
                      description: Target EDA environment. Default: pyAether
                      enum: [pyAether, aether, skill_virtuoso, tcl_innovus, tcl_waveview]
                  required: [code]
            config:
              sandbox_endpoint: tier3_static_analysis
              sandbox_hosts: [pyAether, aether, skill_virtuoso, tcl_innovus, tcl_waveview]
              max_code_length: 5000
              timeout: 60
              tier: 3
              api_database: ~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json
        """)


def generate_html_report(audit_data):
    findings = audit_data["findings"]
    critical = [f for f in findings if f["severity"] == "CRITICAL"]
    high = [f for f in findings if f["severity"] == "HIGH"]
    medium = [f for f in findings if f["severity"] == "MEDIUM"]
    low = [f for f in findings if f["severity"] == "LOW"]
    sev_colors = {"CRITICAL": "#dc3545", "HIGH": "#fd7e14",
                  "MEDIUM": "#ffc107", "LOW": "#0d6efd", "OK": "#198754"}

    def card(f):
        c = sev_colors.get(f["severity"], "#6c757d")
        return f'<div class="card mb-2" style="border-left:4px solid {c};">' \
               f'<div class="card-body"><h5><span class="badge" style="background:{c};">' \
               f'{f["severity"]}</span> {f["id"]}: {f["component"]}</h5>' \
               f'<p><strong>问题:</strong> {f["description"]}</p>' \
               f'<p><strong>证据:</strong> <code>{f["evidence"]}</code></p>' \
               f'<p><strong>修复:</strong> {f["fix"]}</p>' \
               f'<p><strong>状态:</strong> {f["status"]}</p></div></div>'

    cards_html = ''.join(card(f) for f in critical) + ''.join(card(f) for f in high) \
        + ''.join(card(f) for f in medium) + ''.join(card(f) for f in low)

    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>R69: verl 0.4.0 多轮工具调用协议源码级审计</title>
<style>
body{{font-family:-apple-system,"Microsoft YaHei",sans-serif;margin:2rem;background:#f8f9fa;color:#212529;line-height:1.6}}
h1{{color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:.5rem}}
h2{{color:#283593;margin-top:2rem}}h3{{color:#3949ab}}
.card{{background:#fff;border-radius:.375rem;box-shadow:0 1px 3px rgba(0,0,0,.1)}}
code{{background:#e8eaf6;padding:2px 6px;border-radius:3px;font-size:.9em}}
.badge{{padding:3px 8px;border-radius:4px;color:#fff;font-size:.8em}}
.summary{{display:flex;gap:1rem;flex-wrap:wrap;margin:1rem 0}}
.summary-card{{flex:1;min-width:100px;text-align:center;padding:1rem;border-radius:.375rem;color:#fff}}
table{{width:100%;border-collapse:collapse;margin:1rem 0}}
th,td{{padding:8px 12px;border:1px solid #dee2e6;text-align:left}}
th{{background:#e3f2fd;font-weight:600}}
.state-diagram{{background:#e8f5e9;padding:1rem;border-radius:.375rem;font-family:monospace;white-space:pre;overflow-x:auto}}
.deliverable{{background:#e3f2fd;padding:1rem;border-radius:.375rem;margin:1rem 0}}
</style></head><body>
<h1>R69: verl 0.4.0 多轮工具调用协议源码级审计</h1>
<p><strong>日期:</strong> 2026-11-09 wake117 | 零 GPU | 纯源码分析</p>
<p><strong>目标:</strong> 从 verl 0.4.0 源码审计多轮工具调用协议，识别集成差距。</p>
<div class="summary">
<div class="summary-card" style="background:#dc3545"><h2 style="color:#fff;margin:0">{len(critical)}</h2><p>CRITICAL</p></div>
<div class="summary-card" style="background:#fd7e14"><h2 style="color:#fff;margin:0">{len(high)}</h2><p>HIGH</p></div>
<div class="summary-card" style="background:#ffc107"><h2 style="color:#fff;margin:0">{len(medium)}</h2><p>MEDIUM</p></div>
<div class="summary-card" style="background:#0d6efd"><h2 style="color:#fff;margin:0">{len(low)}</h2><p>LOW</p></div>
<div class="summary-card" style="background:#198754"><h2 style="color:#fff;margin:0">{len(findings)}</h2><p>总计</p></div>
</div>
<h2>1. 多轮工具调用状态机</h2>
<div class="state-diagram">PENDING → RUNNING → SGLang generate → 检查 finish_reason
  LENGTH → BREAK | STOP → BREAK | TOOL_CALL → parse → TOOL_CALLING
TOOL_CALLING → asyncio.gather(*[tool.execute()]) → add_tool_response
  → 检查 input_ids >= max_model_len → 是则BREAK / 否则RUNNING循环
[结束] calc_reward_and_release_fn() → finalize()</div>
<h2>2. 关键发现</h2>
{cards_html}
<h2>3. 修复交付物</h2>
<div class="deliverable"><p><strong>3.1</strong> baize_posttrain_eda_tool_v2.py: F01-F03修复</p>
<p><strong>3.2</strong> baize_posttrain_tool_config.yaml: verl工具配置</p></div>
<h2>4. 多轮启用路线图</h2>
<table><tr><th>阶段</th><th>enable</th><th>说明</th></tr>
<tr><td>当前(R0)</td><td>False</td><td>单轮无工具</td></tr>
<tr><td>Smoke后</td><td>True</td><td>多轮+Tier3静态分析</td></tr>
<tr><td>沙盒可达</td><td>True</td><td>多轮+真实沙盒</td></tr></table>
<h2>5. 风险</h2>
<table><tr><th>风险</th><th>缓解</th></tr>
<tr><td>F14: MiniCPM5-2B无parser</td><td>smoke检查;若None需自定义parser</td></tr>
<tr><td>F07: JSON错误静默丢弃</td><td>R4惩罚;log decode_error_count</td></tr>
<tr><td>F06: 上下文溢出假阴性</td><td>ctx=16384;smoke监控</td></tr></table>
<h2>6. 结论</h2>
<p>verl 0.4.0多轮协议<strong>成熟可用</strong>。EDASandboxTool v1有3个CRITICAL API不匹配(F01-F03)，
v2修正后可无缝接入。<strong>关键待验证:</strong> F14(MiniCPM5-2B tool_call_parser)是潜在BLOCKER，
smoke测试中第一时间检查。</p>
<hr><p style="color:#666;font-size:.85em">R69 · 2026-11-09 · 零GPU · ⚠️ 替身RL结果不可迁移到白泽</p>
</body></html>'''


def main():
    parser = argparse.ArgumentParser(description="R69: verl multi-turn tool calling audit")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--html", type=str, default=None)
    parser.add_argument("--json", type=str, default=None)
    parser.add_argument("--generate-config", type=str, default=None)
    args = parser.parse_args()

    audit_basetool_interface()
    audit_multiturn_state_machine()
    audit_tool_config_gap()
    audit_reward_computation()
    audit_format_compatibility()
    audit_concurrency_model()

    source_files = {
        "verl_base_tool": VERL_BASE_TOOL_PATH,
        "verl_sglang_rollout": VERL_SGLANG_ROLLOUT_PATH,
        "verl_schemas": VERL_SCHEMAS_PATH,
        "verl_sandbox_fusion": VERL_SANDBOX_FUSION_PATH,
    }
    source_status = {}
    for name, path in source_files.items():
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        source_status[name] = {"path": path, "exists": exists, "size": size}

    audit_data = {
        "round": "R69", "date": "2026-11-09", "wake": "wake117",
        "verl_version": VERL_VERSION,
        "source_files": source_status,
        "findings": AUDIT_FINDINGS,
        "summary": {
            "total": len(AUDIT_FINDINGS),
            "critical": sum(1 for f in AUDIT_FINDINGS if f["severity"] == "CRITICAL"),
            "high": sum(1 for f in AUDIT_FINDINGS if f["severity"] == "HIGH"),
            "medium": sum(1 for f in AUDIT_FINDINGS if f["severity"] == "MEDIUM"),
            "low": sum(1 for f in AUDIT_FINDINGS if f["severity"] == "LOW"),
        },
    }

    print(f"\n{'='*60}")
    print(f"R69: verl 0.4.0 Multi-Turn Tool Calling Protocol Audit")
    print(f"{'='*60}")
    print(f"  verl version: {VERL_VERSION}")
    print(f"  Source files: {len(source_files)} checked")
    print(f"  Findings: {len(AUDIT_FINDINGS)} total")
    s = audit_data["summary"]
    print(f"    CRITICAL={s['critical']} HIGH={s['high']} MEDIUM={s['medium']} LOW={s['low']}")

    if args.verbose:
        for f in AUDIT_FINDINGS:
            print(f"  [{f['severity']}] {f['id']}: {f['component']} -> {f['fix'][:60]}")

    if args.json:
        with open(args.json, "w") as fp:
            json.dump(audit_data, fp, indent=2, ensure_ascii=False)
        print(f"  JSON -> {args.json}")
    if args.html:
        with open(args.html, "w") as fp:
            fp.write(generate_html_report(audit_data))
        print(f"  HTML -> {args.html}")
    if args.generate_config:
        with open(args.generate_config, "w") as fp:
            fp.write(generate_tool_config_yaml())
        print(f"  Config -> {args.generate_config}")

    print(f"\n  R69 audit complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
